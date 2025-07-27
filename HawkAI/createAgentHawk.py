import vertexai
from vertexai.preview import reasoning_engines
from vertexai.generative_models import GenerativeModel

# Import project constants
from config.constants import PROJECT_ID, LOCATION, MODEL_NAME_PRO, BUCKET_NAME

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

class ProjectHawkAIAgent:
    def __init__(self):
        self.model = GenerativeModel(
            model_name=MODEL_NAME_PRO,
            system_instruction="""You are ProjectHawkAI, an AI agent for proactive event safety monitoring. 
            Your responsibilities include:
            - Analyzing safety conditions at events
            - Identifying potential risks and hazards
            - Providing recommendations for safety improvements
            - Monitoring crowd dynamics and behavior
            - Alerting to emergency situations
            """
        )
        self.chat_session = self.model.start_chat()
    
    def chat(self, message):
        response = self.chat_session.send_message(message)
        return response.text
    
    def analyze_safety_condition(self, condition_description):
        prompt = f"""
        As ProjectHawkAI, analyze the following safety condition at an event:
        
        Condition: {condition_description}
        
        Please provide:
        1. Risk assessment (Low/Medium/High)
        2. Potential consequences
        3. Recommended actions
        4. Monitoring suggestions
        """
        response = self.chat_session.send_message(prompt)
        return response.text

# Create and use the agent
agent = ProjectHawkAIAgent()

# Test the agent
response = agent.chat("Hello, who are you?")
print("Agent Response:", response)

# Example safety analysis
safety_analysis = agent.analyze_safety_condition(
    "Large crowd gathering near the main stage with limited exit routes visible"
)
print("\nSafety Analysis:", safety_analysis)