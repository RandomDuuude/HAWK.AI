# agents/safety_agent.py
import vertexai
from vertexai.generative_models import GenerativeModel
from google.adk.agents import Agent
from typing import Dict, Any

class SafetyMonitoringAgent(Agent):
    """Agent specialized in event safety monitoring and risk assessment"""
    
    def __init__(self, project_id: str, location: str):
        super().__init__(
            name="SafetyMonitoring-Agent",
            description="Specialized agent for event safety monitoring, crowd analysis, and risk assessment",
            instructions="You analyze safety conditions, assess risks, and provide safety recommendations for events."
        )
        vertexai.init(project=project_id, location=location)
        
        self.model = GenerativeModel(
            model_name=MODEL_NAME_FLASH_2,  # Using flash for faster responses
            system_instruction="""
            You are a Safety Monitoring Agent specialized in:
            - Real-time crowd density analysis
            - Emergency exit assessment
            - Weather-related safety risks
            - Infrastructure safety evaluation
            - Incident risk prediction
            
            Always provide structured responses with risk levels (LOW/MEDIUM/HIGH/CRITICAL).
            """
        )
        self.chat_session = self.model.start_chat()
    
    def analyze_crowd_density(self, crowd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crowd density and safety implications"""
        prompt = f"""
        Analyze crowd safety based on this data:
        - Current crowd size: {crowd_data.get('size', 'unknown')}
        - Venue capacity: {crowd_data.get('capacity', 'unknown')}
        - Exit routes available: {crowd_data.get('exits', 'unknown')}
        - Time of day: {crowd_data.get('time', 'unknown')}
        
        Provide JSON response with: risk_level, recommendations, monitoring_priority
        """
        
        response = self.chat_session.send_message(prompt)
        return {
            "agent": "safety_monitoring",
            "analysis_type": "crowd_density",
            "result": response.text,
            "timestamp": crowd_data.get('timestamp')
        }
    
    def assess_weather_risk(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess weather-related safety risks"""
        prompt = f"""
        Evaluate weather safety risks for outdoor event:
        - Conditions: {weather_data.get('conditions', 'unknown')}
        - Temperature: {weather_data.get('temperature', 'unknown')}
        - Wind speed: {weather_data.get('wind_speed', 'unknown')}
        - Precipitation: {weather_data.get('precipitation', 'unknown')}
        
        Focus on risks like: heat exhaustion, hypothermia, wind hazards, lightning.
        Provide JSON response with risk_level and specific precautions.
        """
        
        response = self.chat_session.send_message(prompt)
        return {
            "agent": "safety_monitoring",
            "analysis_type": "weather_risk",
            "result": response.text,
            "conditions": weather_data
        }
