import json
import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel

# Import project constants
from config.constants import PROJECT_ID, LOCATION, MODEL_NAME_FLASH, MODEL_NAME_FLASH_2 as MODEL_NAME

class HawkAIAgent:
    """HawkAI agent for Vertex AI Agent Builder"""
    
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        self.model = GenerativeModel(
            model_name=MODEL_NAME,
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
    
    def analyze_request(self, user_query: str, intent_name: str = "", image_data: str = "") -> str:
        """Analyze user request and provide structured response"""
        try:
            focus_map = {
                "safety": "Focus on crowd safety, infrastructure risks, and immediate hazards",
                "analytics": "Focus on data patterns, trends, and predictive insights", 
                "alert": "Focus on emergency response, prioritization, and escalation",
                "general": "Provide comprehensive safety analysis"
            }
            
            agent_focus = "general"
            for key in focus_map.keys():
                if key in intent_name.lower():
                    agent_focus = key
                    break
            
            prompt = f"""
            Request: {user_query}
            Focus: {focus_map[agent_focus]}
            {f'Image Data: {image_data}' if image_data else ''}
            
            Provide structured analysis for HawkAI event safety monitoring.
            """
            
            response = self.chat_session.send_message(prompt)
            return response.text
            
        except Exception as e:
            return f"🚨 HawkAI Analysis Error: {str(e)}. Please provide more details or try again."

# Initialize agent
agent = HawkAIAgent()

@functions_framework.http
def projectHawkAI_handler(request):
    """Cloud Function entry point for Vertex AI Agent Builder webhook"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    try:
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            
            if not request_json:
                return json.dumps({
                    "fulfillment_response": {
                        "messages": [{"text": {"text": ["No request data received"]}}]
                    }
                }), 400, headers
            
            # Extract user query and intent
            user_query = ""
            intent_name = ""
            
            if 'text' in request_json:
                user_query = request_json['text']
            elif 'queryResult' in request_json:
                user_query = request_json['queryResult'].get('queryText', '')
                intent_name = request_json['queryResult'].get('intent', {}).get('displayName', '')
            elif 'query' in request_json:
                user_query = request_json['query']

            request_image = ""
            if 'image' in request_json:
                # Process image bytes to JPEG
                import base64
                import io
                from PIL import Image
                
                try:
                    # Decode base64 image data if it's in that format
                    if isinstance(request_json['image'], str) and request_json['image'].startswith('data:image'):
                        # Extract the base64 part
                        image_data = request_json['image'].split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                    else:
                        # Assume it's already bytes
                        image_bytes = request_json['image']
                    
                    # Create image from bytes
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Process image (resize if needed)
                    max_size = (1024, 1024)  # Maximum dimensions
                    image.thumbnail(max_size, Image.LANCZOS)
                    
                    # Save processed image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG')
                    
                    # Convert back to base64 for model input
                    processed_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                    request_image = f"data:image/jpeg;base64,{processed_image}"
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    request_image = "[Error processing image]"
            
            if not user_query:
                user_query = "General safety status check"
            
            # Process with HawkAI agent
            response_text = agent.analyze_request(user_query, intent_name, request_image)
            
            # Return Dialogflow compatible response
            response_data = {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [response_text]
                            }
                        }
                    ]
                }
            }
            
            return json.dumps(response_data), 200, headers
        
        else:
            return json.dumps({"error": "Only POST method supported"}), 405, headers
            
    except Exception as e:
        error_response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"🚨 HawkAI System Error: {str(e)}"]
                        }
                    }
                ]
            }
        }
        
        return json.dumps(error_response), 500, headers