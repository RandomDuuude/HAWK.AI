# fast_main.py - Ultra-fast version with Gemini Flash
import asyncio
import json
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel
from typing import Dict, Any

# Import project constants
from config.constants import PROJECT_ID, LOCATION, MODEL_NAME_FLASH, MODEL_NAME_FLASH_2, MODEL_NAME_FLASH_2

class FastCoordinatorAgent:
    """
    Ultra-fast coordinator using Gemini Flash for sub-second responses
    """
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Use Gemini Flash for speed
        self.model = GenerativeModel(
            model_name=MODEL_NAME_FLASH,
            system_instruction="""
            You are ProjectHawkAI - AI for event safety monitoring.
            
            STRICT FORMAT (under 150 words):
            
            🛡️ SAFETY: [Risk: LOW/MED/HIGH] [Main concern] [Action needed]
            📊 DATA: [Key metric to watch] [Pattern/trend if any]  
            🚨 ALERT: [Priority: P1-P4] [Response time] [Escalate: Y/N]
            
            💡 RECOMMENDATION: [1-2 sentence action plan]
            
            Be extremely concise. No fluff. Safety first.
            """
        )
        
        self.chat_session = self.model.start_chat()
        self.conversation_history = []
    
    async def process_request(self, user_prompt: str) -> Dict[str, Any]:
        """
        Process request with minimal latency
        """
        start_time = datetime.now()
        
        # Minimal prompt for speed
        prompt = f"Analyze: {user_prompt}"
        
        try:
            response = self.chat_session.send_message(prompt)
            
            result = {
                "user_request": user_prompt,
                "response": response.text,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
                "model": MODEL_NAME_FLASH_2
            }
            
            self.conversation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "user_request": user_prompt,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

class FastProjectHawkAISystem:
    """
    Ultra-fast ProjectHawkAI system
    """
    
    def __init__(self):
        self.coordinator = FastCoordinatorAgent(PROJECT_ID, LOCATION)
        self.session_history = []
    
    async def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Process prompt with speed optimization
        """
        print(f"\n⚡ ProjectHawkAI FastMode: '{user_prompt}'")
        print("=" * 50)
        
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
            
            print(f"❌ Error: {e}")
            return error_result
    
    def _display_results(self, result: Dict[str, Any]):
        """Display results optimized for speed"""
        print(f"⚡ Response Time: {result['processing_time']:.2f}s")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"\n{result['response']}")
        print("-" * 50)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        if not self.session_history:
            return {"message": "No requests processed yet"}
        
        total_requests = len(self.session_history)
        avg_processing_time = sum(r['processing_time'] for r in self.session_history) / total_requests
        
        return {
            "total_requests": total_requests,
            "average_processing_time": f"{avg_processing_time:.2f}s",
            "model_used": MODEL_NAME_FLASH_2,
            "session_start": self.session_history[0]['timestamp'] if self.session_history else None
        }

async def main():
    """
    Fast demo
    """
    print("⚡ ProjectHawkAI FastMode - Optimized for Speed")
    
    system = FastProjectHawkAISystem()
    
    # Quick test prompts
    test_prompts = [
        "5000 people in 3000 capacity venue",
        "Fire alarm sector A, medical emergency gate 3",
        "Rain forecast 25mph winds tomorrow outdoor event",
        "Unusual incident patterns this week",
        "Need evacuation plan severe weather"
    ]
    
    print("⚡ Processing tests at high speed...\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"🔥 TEST {i}")
        await system.process_prompt(prompt)
        await asyncio.sleep(0.5)  # Minimal delay
    
    print(f"\n📊 SESSION STATS")
    summary = system.get_session_summary()
    print(json.dumps(summary, indent=2))

async def interactive_mode():
    """
    Fast interactive mode
    """
    print("⚡ ProjectHawkAI FastMode Interactive")
    print("Commands: 'exit', 'summary', or enter your safety query\n")
    
    system = FastProjectHawkAISystem()
    
    while True:
        try:
            user_input = input("\n⚡ Query: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 FastMode closed!")
                break
            elif user_input.lower() == 'summary':
                summary = system.get_session_summary()
                print(json.dumps(summary, indent=2))
                continue
            elif not user_input:
                continue
            
            await system.process_prompt(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 FastMode closed!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())