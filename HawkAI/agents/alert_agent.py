from google.adk.agents import Agent
from typing import Dict, Any

# agents/alert_agent.py
class AlertManagementAgent(Agent):
    """Agent specialized in alert management and emergency response coordination"""
    
    def __init__(self, project_id: str, location: str):
        super().__init__(
            name="AlertManagement-Agent",
            description="Specialized agent for alert management, emergency response coordination, and incident handling", 
            instructions="You manage alerts, prioritize emergencies, and coordinate response plans for incidents."
        )
        vertexai.init(project=project_id, location=location)
        
        self.model = GenerativeModel(
            model_name=MODEL_NAME_FLASH_2,
            system_instruction="""
            You are an Alert Management Agent specialized in:
            - Emergency alert prioritization
            - Response protocol recommendations
            - Communication strategy optimization
            - Escalation pathway management
            - Resource allocation for incidents
            
            Always prioritize human safety and provide clear, actionable guidance.
            """
        )
        self.chat_session = self.model.start_chat()
    
    def prioritize_alerts(self, alerts: list) -> Dict[str, Any]:
        """Prioritize multiple alerts based on severity and impact"""
        prompt = f"""
        Prioritize these safety alerts:
        Alerts: {alerts}
        
        For each alert, determine:
        1. Priority level (P1-Critical, P2-High, P3-Medium, P4-Low)
        2. Required response time
        3. Resource requirements
        4. Escalation needs
        
        Provide ranked list with justifications.
        """
        
        response = self.chat_session.send_message(prompt)
        return {
            "agent": "alert_management",
            "analysis_type": "alert_prioritization",
            "result": response.text,
            "alerts_processed": len(alerts)
        }
    
    def generate_response_plan(self, incident_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate emergency response plan"""
        prompt = f"""
        Generate emergency response plan for:
        Incident: {incident_details}
        
        Include:
        1. Immediate actions (0-5 minutes)
        2. Short-term response (5-30 minutes)
        3. Extended response (30+ minutes)
        4. Communication protocols
        5. Resource deployment strategy
        
        Ensure plan is specific and actionable.
        """
        
        response = self.chat_session.send_message(prompt)
        return {
            "agent": "alert_management", 
            "analysis_type": "response_planning",
            "result": response.text,
            "incident_type": incident_details.get('type', 'unknown')
        }
