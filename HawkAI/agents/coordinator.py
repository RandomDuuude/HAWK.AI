import vertexai
from vertexai.generative_models import GenerativeModel
from google.adk.agents import Agent
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

from .safety_agent import SafetyMonitoringAgent
from .analytics_agent import DataAnalyticsAgent
from .alert_agent import AlertManagementAgent
from config.agent_config import AGENT_CONFIGS, get_agent_for_query

class CoordinatorAgent(Agent):
    """
    Main coordinator agent using Gemini 1.5 Pro that routes requests 
    to specialized agents and aggregates responses
    """
    
    def __init__(self, project_id: str, location: str):
        super().__init__(
            name="ProjectHawkAI-Coordinator",
            description="Main coordinator agent for event safety monitoring that routes requests to specialized agents",
            instructions="You are the main coordinator for ProjectHawkAI. Route requests to appropriate specialist agents and synthesize their responses."
        )
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize the coordinator model (Gemini Pro for complex reasoning)
        self.model = GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction="""
            You are ProjectHawkAI Coordinator, the main AI agent for proactive event safety monitoring.
            
            Your role is to:
            1. Analyze incoming user requests and determine the best approach
            2. Route requests to specialized agents when needed
            3. Coordinate multiple agents for complex queries
            4. Synthesize responses from specialist agents into coherent answers
            5. Provide direct responses for simple queries
            
            Available specialist agents:
            - SafetyMonitoringAgent: Real-time safety assessment, crowd analysis, weather risks
            - DataAnalyticsAgent: Pattern analysis, anomaly detection, predictive modeling  
            - AlertManagementAgent: Emergency response, alert prioritization, escalation
            
            Always prioritize safety and provide actionable insights.
            When routing to agents, explain your reasoning.
            When synthesizing multiple agent responses, highlight key insights and conflicts.
            """
        )
        
        # Initialize specialist agents
        self.specialist_agents = {
            'safety_monitoring': SafetyMonitoringAgent(project_id, location),
            'data_analytics': DataAnalyticsAgent(project_id, location),
            'alert_management': AlertManagementAgent(project_id, location)
        }
        
        # Start chat session
        self.chat_session = self.model.start_chat()
        
        # Track conversation context
        self.conversation_history = []
    
    def analyze_request(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analyze user request to determine routing strategy
        """
        analysis_prompt = f"""
        Analyze this user request for ProjectHawkAI event safety monitoring:
        
        User Request: "{user_prompt}"
        
        Determine:
        1. Request type (safety_assessment, data_analysis, alert_management, general_query)
        2. Complexity level (simple, moderate, complex)
        3. Required specialist agents (list of agent names)
        4. Priority level (low, medium, high, critical)
        5. Expected response time (seconds)
        
        Respond in JSON format:
        {{
            "request_type": "",
            "complexity": "",
            "required_agents": [],
            "priority": "", 
            "expected_response_time": 0,
            "reasoning": ""
        }}
        """
        
        response = self.chat_session.send_message(analysis_prompt)
        
        try:
            analysis = json.loads(response.text.strip('```json\n```'))
        except json.JSONDecodeError:
            # Fallback to keyword-based routing
            primary_agent = get_agent_for_query(user_prompt)
            analysis = {
                "request_type": "fallback_routing",
                "complexity": "moderate", 
                "required_agents": [primary_agent],
                "priority": "medium",
                "expected_response_time": 5,
                "reasoning": f"JSON parsing failed, using keyword-based routing to {primary_agent}"
            }
        
        return analysis
    
    async def route_to_agents(self, user_prompt: str, required_agents: List[str], 
                            request_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to required specialist agents
        """
        agent_responses = {}
        
        for agent_name in required_agents:
            if agent_name in self.specialist_agents:
                try:
                    agent = self.specialist_agents[agent_name]
                    
                    # Route to appropriate method based on agent type and request
                    if agent_name == 'safety_monitoring':
                        if 'crowd' in user_prompt.lower():
                            # Extract crowd data from prompt or use defaults
                            crowd_data = self._extract_crowd_data(user_prompt)
                            response = agent.analyze_crowd_density(crowd_data)
                        elif 'weather' in user_prompt.lower():
                            weather_data = self._extract_weather_data(user_prompt)
                            response = agent.assess_weather_risk(weather_data)
                        else:
                            # General safety analysis
                            response = {
                                "agent": "safety_monitoring",
                                "analysis_type": "general_safety",
                                "result": f"General safety analysis for: {user_prompt}",
                                "timestamp": datetime.now().isoformat()
                            }
                    
                    elif agent_name == 'data_analytics':
                        if 'historical' in user_prompt.lower() or 'pattern' in user_prompt.lower():
                            incident_data = self._extract_incident_data(user_prompt)
                            response = agent.analyze_historical_patterns(incident_data)
                        else:
                            current_metrics = self._extract_metrics_data(user_prompt)
                            response = agent.detect_anomalies(current_metrics)
                    
                    elif agent_name == 'alert_management':
                        if 'prioritize' in user_prompt.lower() or 'alerts' in user_prompt.lower():
                            alerts = self._extract_alerts_data(user_prompt)
                            response = agent.prioritize_alerts(alerts)
                        else:
                            incident_details = self._extract_incident_details(user_prompt)
                            response = agent.generate_response_plan(incident_details)
                    
                    agent_responses[agent_name] = response
                    
                except Exception as e:
                    agent_responses[agent_name] = {
                        "agent": agent_name,
                        "error": f"Agent execution failed: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
        
        return agent_responses
    
    def synthesize_responses(self, user_prompt: str, agent_responses: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> str:
        """
        Synthesize responses from specialist agents into a coherent answer
        """
        synthesis_prompt = f"""
        Original user request: "{user_prompt}"
        
        Request analysis: {json.dumps(analysis, indent=2)}
        
        Specialist agent responses:
        {json.dumps(agent_responses, indent=2)}
        
        Synthesize these responses into a coherent, actionable answer that:
        1. Directly addresses the user's request
        2. Highlights key insights from each agent
        3. Identifies any conflicts or contradictions
        4. Provides clear recommendations
        5. Indicates confidence levels where appropriate
        
        Keep the response concise but comprehensive.
        """
        
        response = self.chat_session.send_message(synthesis_prompt)
        return response.text
    
    async def process_request(self, user_prompt: str) -> Dict[str, Any]:
        """
        Main method to process user requests through the multi-agent system
        """
        start_time = datetime.now()
        
        # Step 1: Analyze the request
        analysis = self.analyze_request(user_prompt)
        
        # Step 2: Route to specialist agents
        agent_responses = await self.route_to_agents(
            user_prompt, 
            analysis['required_agents'],
            analysis
        )
        
        # Step 3: Synthesize responses
        final_response = self.synthesize_responses(user_prompt, agent_responses, analysis)
        
        # Step 4: Prepare comprehensive result
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            "user_request": user_prompt,
            "analysis": analysis,
            "agent_responses": agent_responses,
            "final_response": final_response,
            "processing_time": processing_time,
            "timestamp": end_time.isoformat(),
            "agents_used": list(agent_responses.keys())
        }
        
        # Update conversation history
        self.conversation_history.append(result)
        
        return result
    
    # Helper methods to extract structured data from natural language prompts
    def _extract_crowd_data(self, prompt: str) -> Dict[str, Any]:
        """Extract crowd-related data from user prompt"""
        return {
            "size": "unknown",
            "capacity": "unknown", 
            "exits": "unknown",
            "time": datetime.now().strftime("%H:%M"),
            "timestamp": datetime.now().isoformat(),
            "raw_prompt": prompt
        }
    
    def _extract_weather_data(self, prompt: str) -> Dict[str, Any]:
        """Extract weather-related data from user prompt"""
        return {
            "conditions": "unknown",
            "temperature": "unknown",
            "wind_speed": "unknown", 
            "precipitation": "unknown",
            "raw_prompt": prompt
        }
    
    def _extract_incident_data(self, prompt: str) -> Dict[str, Any]:
        """Extract incident data from user prompt"""
        return {
            "incidents": [],
            "time_period": "unknown",
            "raw_prompt": prompt
        }
    
    def _extract_metrics_data(self, prompt: str) -> Dict[str, Any]:
        """Extract metrics data from user prompt"""
        return {
            "crowd_density": "unknown",
            "response_times": "unknown",
            "resource_utilization": "unknown",
            "raw_prompt": prompt
        }
    
    def _extract_alerts_data(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract alerts from user prompt"""
        return [
            {
                "id": "sample_alert",
                "type": "general",
                "severity": "medium", 
                "description": prompt,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _extract_incident_details(self, prompt: str) -> Dict[str, Any]:
        """Extract incident details from user prompt"""
        return {
            "type": "general_incident",
            "location": "unknown",
            "severity": "medium",
            "description": prompt,
            "timestamp": datetime.now().isoformat()
        }