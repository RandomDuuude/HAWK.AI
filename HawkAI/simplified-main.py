# simplified_main.py
import asyncio
import json
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel

from google.adk.agents import Agent
from typing import Dict, Any

# Import project constants
from config.constants import PROJECT_ID, LOCATION, MODEL_NAME_PRO

class SimpleCoordinatorAgent:
    """
    Simplified coordinator agent that works without ADK dependencies
    """
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize the coordinator model
        self.model = GenerativeModel(
            model_name=MODEL_NAME_PRO,
            system_instruction="""
            You are ProjectHawkAI Coordinator, an AI agent for proactive event safety monitoring.
            
            RESPONSE FORMAT: Keep responses concise and structured. Use bullet points. Limit to 200-300 words total.
            
            For each request, provide analysis covering:
            
            🛡️ SAFETY ASSESSMENT:
            • Risk level (LOW/MEDIUM/HIGH/CRITICAL)
            • Key safety concerns (max 2-3 points)
            • Immediate actions needed
            
            📊 DATA INSIGHTS:
            • Relevant patterns or metrics
            • Monitoring recommendations
            
            🚨 ALERT MANAGEMENT:
            • Priority level (P1-P4)
            • Response timeline
            • Escalation if needed
            
            Be direct, actionable, and safety-focused. Avoid lengthy explanations.
            """
        )
        
        self.chat_session = self.model.start_chat()
        self.conversation_history = []
    
    async def process_request(self, user_prompt: str) -> Dict[str, Any]:
        """
        Process user request through the coordinator
        """
        start_time = datetime.now()
        
        # Analyze which agent logic would be invoked
        agent_analysis = self._analyze_agent_routing(user_prompt)
        
        # Enhanced prompt that simulates multi-agent analysis
        enhanced_prompt = f"""
        Request: "{user_prompt}"
        
        Provide concise analysis (under 250 words):
        
        🛡️ SAFETY: Risk level and key concerns
        📊 DATA: Relevant metrics and patterns  
        🚨 ALERTS: Priority and response needed
        
        Be brief and actionable.
        """
        
        try:
            response = self.chat_session.send_message(enhanced_prompt)
            
            result = {
                "user_request": user_prompt,
                "coordinator_response": response.text,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "comprehensive",
                "agent_routing": agent_analysis  # Added agent routing info
            }
            
            self.conversation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "user_request": user_prompt,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "agent_routing": agent_analysis
            }
    
    def _analyze_agent_routing(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analyze which agents would be invoked for this request
        """
        query_lower = user_prompt.lower()
        
        # Define agent keywords
        safety_keywords = [
            "crowd", "density", "exit", "emergency", "evacuation", "weather", 
            "risk", "hazard", "incident", "safety", "danger", "capacity", "overflow"
        ]
        
        analytics_keywords = [
            "pattern", "trend", "historical", "predict", "anomaly", "analysis",
            "statistics", "data", "metrics", "performance", "unusual", "week", "month"
        ]
        
        alert_keywords = [
            "alert", "priority", "response", "escalate", "urgent", "critical",
            "emergency", "notification", "protocol", "fire", "medical", "evacuation"
        ]
        
        # Count matches
        safety_matches = [kw for kw in safety_keywords if kw in query_lower]
        analytics_matches = [kw for kw in analytics_keywords if kw in query_lower]
        alert_matches = [kw for kw in alert_keywords if kw in query_lower]
        
        # Determine primary and secondary agents
        scores = {
            "safety_monitoring": len(safety_matches),
            "data_analytics": len(analytics_matches),
            "alert_management": len(alert_matches)
        }
        
        # Get agents with non-zero scores
        invoked_agents = {k: v for k, v in scores.items() if v > 0}
        primary_agent = max(scores, key=scores.get) if max(scores.values()) > 0 else "safety_monitoring"
        
        return {
            "primary_agent": primary_agent,
            "invoked_agents": invoked_agents,
            "keyword_matches": {
                "safety": safety_matches,
                "analytics": analytics_matches,
                "alerts": alert_matches
            },
            "routing_confidence": max(scores.values()) / len(query_lower.split()) if query_lower.split() else 0
        }

class SimpleProjectHawkAISystem:
    """
    Simplified ProjectHawkAI system for testing
    """
    
    def __init__(self):
        self.coordinator = SimpleCoordinatorAgent(PROJECT_ID, LOCATION)
        self.session_history = []
    
    async def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Process a user prompt through the system
        """
        print(f"\n🤖 ProjectHawkAI Processing: '{user_prompt}'")
        print("=" * 60)
        
        try:
            result = await self.coordinator.process_request(user_prompt)
            
            self._display_results(result)
            self.session_history.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "user_request": user_prompt,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time": 0
            }
            
            print(f"❌ Error processing request: {e}")
            return error_result
    
    def _display_results(self, result: Dict[str, Any]):
        """Display results"""
        
        # Display agent routing information
        if 'agent_routing' in result:
            routing = result['agent_routing']
            print(f"🎯 Agent Routing:")
            print(f"   Primary Agent: {routing['primary_agent']}")
            print(f"   Invoked Agents: {list(routing['invoked_agents'].keys())}")
            print(f"   Confidence: {routing['routing_confidence']:.2f}")
            
            # Show keyword matches for debugging
            matches = routing['keyword_matches']
            if any(matches.values()):
                print(f"   Keywords: Safety({len(matches['safety'])}), Analytics({len(matches['analytics'])}), Alerts({len(matches['alerts'])})")
        
        print(f"⏱️  Processing Time: {result['processing_time']:.2f} seconds")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"\n💡 ProjectHawkAI Analysis:")
        print("-" * 40)
        print(result['coordinator_response'])
        print("-" * 40)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        if not self.session_history:
            return {"message": "No requests processed yet"}
        
        total_requests = len(self.session_history)
        avg_processing_time = sum(r['processing_time'] for r in self.session_history) / total_requests
        
        return {
            "total_requests": total_requests,
            "average_processing_time": avg_processing_time,
            "session_start": self.session_history[0]['timestamp'] if self.session_history else None,
            "latest_request": self.session_history[-1]['timestamp'] if self.session_history else None
        }

async def main():
    """
    Main demo function
    """
    print("🚀 Initializing ProjectHawkAI System (Simplified Version)...")
    
    system = SimpleProjectHawkAISystem()
    
    # Test prompts
    test_prompts = [
        "Analyze the crowd density at the main stage - there are about 5000 people in a space meant for 3000",
        
        "We're seeing unusual patterns in incident reports over the past week. Can you analyze this?",
        
        "Multiple alerts: fire alarm in sector A, medical emergency near gate 3, overcrowding at food court. What should we do?",
        
        "What's the weather risk for our outdoor event tomorrow? Rain forecast with 25 mph winds.",
        
        "Generate an emergency response plan for potential evacuation due to severe weather."
    ]
    
    print("✅ System initialized. Processing test prompts...\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*20} TEST {i} {'='*20}")
        await system.process_prompt(prompt)
        await asyncio.sleep(1)
    
    # Display session summary
    print(f"\n{'='*20} SESSION SUMMARY {'='*20}")
    summary = system.get_session_summary()
    print(json.dumps(summary, indent=2))

async def interactive_mode():
    """
    Interactive mode for testing
    """
    print("🚀 ProjectHawkAI Interactive Mode (Simplified)")
    print("Type 'exit' to quit, 'summary' for session summary\n")
    
    system = SimpleProjectHawkAISystem()
    
    while True:
        try:
            user_input = input("\n🎯 Enter your prompt: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'summary':
                summary = system.get_session_summary()
                print(json.dumps(summary, indent=2))
                continue
            elif not user_input:
                continue
            
            await system.process_prompt(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())