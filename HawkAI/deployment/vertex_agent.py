import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform
from typing import Dict, Any, List
import json

# Import project constants
from config.constants import PROJECT_ID, LOCATION

# Agent configuration
AGENT_NAME = "projectHawkAI-safety-monitor"

class VertexAgentDeployer:
    """
    Deploy ProjectHawkAI multi-agent system to Vertex AI Agent Builder
    """
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
    
    def create_agent_config(self) -> Dict[str, Any]:
        """
        Create agent configuration for Vertex AI Agent Builder
        """
        return {
            "display_name": "ProjectHawkAI Safety Monitor",
            "description": "Multi-agent system for proactive event safety monitoring and emergency response",
            "agent_human_config": {
                "human_agent_assignment_config": {
                    "human_agent_assignment": "HUMAN_AGENT_ASSIGNMENT_OPTIONAL"
                }
            },
            "start_flow": "projects/{}/locations/{}/agents/{}/flows/00000000-0000-0000-0000-000000000000".format(
                PROJECT_ID, LOCATION, AGENT_NAME
            ),
            "security_settings": f"projects/{PROJECT_ID}/locations/{LOCATION}/securitySettings/default",
            "enable_stackdriver_logging": True,
            "enable_spell_check": True,
            "supported_language_codes": ["en"],
            "time_zone": "Asia/Kolkata",
            "advanced_settings": {
                "logging_settings": {
                    "enable_stackdriver_logging": True,
                    "enable_interaction_logging": True
                }
            }
        }
    
    def create_intents(self) -> List[Dict[str, Any]]:
        """
        Create intents for different agent functionalities
        """
        return [
            {
                "display_name": "safety.crowd.analysis",
                "description": "Handle crowd density and safety analysis requests",
                "training_phrases": [
                    {"parts": [{"text": "analyze crowd density"}]},
                    {"parts": [{"text": "check crowd safety"}]},
                    {"parts": [{"text": "overcrowding situation"}]},
                    {"parts": [{"text": "people capacity exceeded"}]},
                    {"parts": [{"text": "venue safety assessment"}]}
                ],
                "messages": [
                    {
                        "text": {
                            "text": ["I'll analyze the crowd safety situation. Please provide details about the current crowd size, venue capacity, and location."]
                        }
                    }
                ]
            },
            {
                "display_name": "analytics.pattern.analysis", 
                "description": "Handle data analysis and pattern recognition requests",
                "training_phrases": [
                    {"parts": [{"text": "analyze historical patterns"}]},
                    {"parts": [{"text": "detect anomalies"}]},
                    {"parts": [{"text": "unusual incidents"}]},
                    {"parts": [{"text": "trend analysis"}]},
                    {"parts": [{"text": "data insights"}]}
                ],
                "messages": [
                    {
                        "text": {
                            "text": ["I'll analyze the data patterns for you. Please share the incident data or metrics you'd like me to examine."]
                        }
                    }
                ]
            },
            {
                "display_name": "alert.emergency.management",
                "description": "Handle emergency alerts and response coordination",
                "training_phrases": [
                    {"parts": [{"text": "emergency alert"}]},
                    {"parts": [{"text": "fire alarm"}]},
                    {"parts": [{"text": "medical emergency"}]},
                    {"parts": [{"text": "evacuation needed"}]},
                    {"parts": [{"text": "urgent response required"}]}
                ],
                "messages": [
                    {
                        "text": {
                            "text": ["🚨 Emergency detected! I'm prioritizing this alert. Please provide immediate details about the situation."]
                        }
                    }
                ]
            }
        ]
    
    def create_fulfillment_webhook(self) -> str:
        """
        Create webhook configuration for agent fulfillment
        """
        webhook_config = {
            "display_name": "ProjectHawkAI-Webhook",
            "generic_web_service": {
                "uri": f"https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/projectHawkAI-handler",
                "username": "",
                "password": "",
                "request_headers": {
                    "Content-Type": "application/json"
                },
                "allowed_ca_certs": []
            },
            "timeout": "30s",
            "disabled": False
        }
        
        return json.dumps(webhook_config, indent=2)

class ProjectHawkAIAgentHandler:
    """
    Cloud Function handler for ProjectHawkAI agent
    """
    
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Initialize the coordinator model
        self.model = GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction="""
            You are ProjectHawkAI Coordinator for Vertex AI Agent Builder.
            
            RESPONSE FORMAT (under 300 words):
            
            🛡️ SAFETY ASSESSMENT:
            • Risk level: [LOW/MEDIUM/HIGH/CRITICAL]
            • Key concerns: [2-3 main points]
            • Immediate actions: [specific steps]
            
            📊 DATA INSIGHTS:
            • Relevant metrics: [what to monitor]
            • Patterns detected: [if any]
            • Predictions: [if applicable]
            
            🚨 ALERT STATUS:
            • Priority: [P1-P4]
            • Response time: [immediate/minutes/hours]
            • Escalation: [yes/no with reason]
            
            💡 RECOMMENDATIONS:
            [2-3 specific actionable items]
            
            Always prioritize safety. Be concise but comprehensive.
            """
        )
        
        self.chat_session = self.model.start_chat()
    
    def handle_webhook_request(self, request_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming webhook requests from Vertex AI Agent
        """
        try:
            # Extract user query from Dialogflow CX request
            user_query = request_json.get('text', '')
            session_id = request_json.get('session', '')
            intent_name = request_json.get('intentInfo', {}).get('displayName', '')
            
            # Route to appropriate analysis based on intent
            if 'safety' in intent_name.lower():
                agent_type = "safety_monitoring"
            elif 'analytics' in intent_name.lower():
                agent_type = "data_analytics" 
            elif 'alert' in intent_name.lower():
                agent_type = "alert_management"
            else:
                agent_type = "general"
            
            # Process with coordinator
            enhanced_prompt = f"""
            Intent: {intent_name}
            Agent Type: {agent_type}
            User Query: {user_query}
            
            Provide structured analysis focusing on the {agent_type} perspective.
            """
            
            response = self.chat_session.send_message(enhanced_prompt)
            
            # Return Dialogflow CX response format
            return {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [response.text]
                            }
                        }
                    ]
                },
                "session_info": {
                    "parameters": {
                        "agent_type": agent_type,
                        "processing_time": "< 3s"
                    }
                }
            }
            
        except Exception as e:
            return {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [f"🚨 ProjectHawkAI Error: {str(e)}. Please try again or contact support."]
                            }
                        }
                    ]
                }
            }

# Cloud Function entry point
def projectHawkAI_handler(request):
    """
    Cloud Function entry point for Vertex AI Agent webhook
    """
    handler = ProjectHawkAIAgentHandler()
    
    if request.method == 'POST':
        request_json = request.get_json()
        return handler.handle_webhook_request(request_json)
    else:
        return {"error": "Only POST method supported"}, 405

# Deployment script
def deploy_to_vertex_ai():
    """
    Deploy ProjectHawkAI to Vertex AI Agent Builder
    """
    deployer = VertexAgentDeployer()
    
    print("🚀 Starting ProjectHawkAI deployment to Vertex AI Agent Builder...")
    
    # Step 1: Create agent configuration
    agent_config = deployer.create_agent_config()
    print("✅ Agent configuration created")
    
    # Step 2: Create intents
    intents = deployer.create_intents()
    print(f"✅ Created {len(intents)} intents")
    
    # Step 3: Create webhook configuration
    webhook_config = deployer.create_fulfillment_webhook()
    print("✅ Webhook configuration created")
    
    # Step 4: Generate deployment commands
    print("\n📋 Manual Deployment Steps:")
    print("=" * 50)
    
    print("1. Enable APIs:")
    print(f"   gcloud services enable dialogflow.googleapis.com --project={PROJECT_ID}")
    print(f"   gcloud services enable cloudfunctions.googleapis.com --project={PROJECT_ID}")
    
    print("\n2. Deploy Cloud Function:")
    print("   gcloud functions deploy projectHawkAI-handler \\")
    print("     --runtime python311 \\")
    print("     --trigger-http \\")
    print("     --entry-point projectHawkAI_handler \\")
    print("     --memory 512MB \\")
    print("     --timeout 30s \\")
    print(f"     --region {LOCATION} \\")
    print(f"     --project {PROJECT_ID}")
    
    print("\n3. Go to Vertex AI Agent Builder Console:")
    print(f"   https://console.cloud.google.com/vertex-ai/agents?project={PROJECT_ID}")
    
    print("\n4. Create New Agent with:")
    print("   - Name: ProjectHawkAI Safety Monitor")
    print("   - Description: Multi-agent system for event safety monitoring")
    print("   - Language: English")
    print(f"   - Region: {LOCATION}")
    
    print("\n5. Import intents and configure webhook URL:")
    print(f"   https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/projectHawkAI-handler")
    
    print("\n✅ Configuration files generated successfully!")
    
    # Save configurations to files
    with open('agent_config.json', 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    with open('intents.json', 'w') as f:
        json.dump(intents, f, indent=2)
    
    with open('webhook_config.json', 'w') as f:
        json.dump(json.loads(webhook_config), f, indent=2)
    
    print("\n📁 Configuration files saved:")
    print("   - agent_config.json")
    print("   - intents.json") 
    print("   - webhook_config.json")

if __name__ == "__main__":
    deploy_to_vertex_ai()