#!/bin/bash

# === Vertex AI Agent Builder Deployment Script for HawkAI ===

PROJECT_ID="hawkai-467107"
LOCATION="global"
AGENT_DISPLAY_NAME="HawkAI-Safety-Monitor"
SERVICE_ACCOUNT_NAME="hawkai-agent"
KEY_FILE="hawkai-key.json"

echo "🚀 Deploying HawkAI with Vertex AI Agent Builder"

# --- Check / Create Service Account ---
echo "🔐 Checking service account..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --project=$PROJECT_ID &>/dev/null; then
    echo "Creating service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --project=$PROJECT_ID
fi

# Assign required roles (idempotent)
for role in roles/dialogflow.admin roles/aiplatform.admin roles/serviceusage.serviceUsageAdmin; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="$role" --quiet
done

# Create key file if missing
if [ ! -f "$KEY_FILE" ]; then
    echo "🔑 Creating service account key..."
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
fi

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/$KEY_FILE"

# --- Enable APIs ---
echo "📡 Enabling required APIs..."
gcloud services enable \
    aiplatform.googleapis.com \
    dialogflow.googleapis.com \
    discoveryengine.googleapis.com \
    --project=$PROJECT_ID

sleep 10

# --- Find existing agent ---
ACCESS_TOKEN=$(gcloud auth application-default print-access-token)

echo "🔍 Checking for existing agent..."
LIST_RESPONSE=$(curl -s -X GET \
  "https://dialogflow.googleapis.com/v3/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

AGENT_NAME=$(echo "$LIST_RESPONSE" | jq -r --arg DISPLAY "$AGENT_DISPLAY_NAME" '.agents[] | select(.displayName==$DISPLAY) | .name' | head -n1)

# --- Create agent if not found ---
if [ -z "$AGENT_NAME" ]; then
    echo "🤖 No existing agent found. Creating new agent..."

    cat > agent_config.json << EOF
{
  "displayName": "$AGENT_DISPLAY_NAME",
  "defaultLanguageCode": "en",
  "timeZone": "Asia/Kolkata",
  "description": "HawkAI Safety Monitoring Agent for proactive event safety analysis",
  "enableStackdriverLogging": true,
  "apiVersion": "API_VERSION_V3_BETA",
  "tier": "TIER_STANDARD"
}
EOF

    CREATE_RESPONSE=$(curl -s -X POST \
      "https://dialogflow.googleapis.com/v3/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d @agent_config.json)

    AGENT_NAME=$(echo "$CREATE_RESPONSE" | jq -r '.name // empty')

    if [ -z "$AGENT_NAME" ]; then
        echo "❌ Failed to create agent. Response: $CREATE_RESPONSE"
        exit 1
    fi

    echo "✅ Created new agent: $AGENT_NAME"
    rm -f agent_config.json
else
    echo "✅ Reusing existing agent: $AGENT_NAME"
fi

echo "🎉 Deployment complete. Service account and agent reused where possible."

# #!/bin/bash

# # Vertex AI Agent Builder Deployment Script for HawkAI
# PROJECT_ID="hawkai-467107"
# LOCATION="global"  # Agent Builder typically uses global
# AGENT_DISPLAY_NAME="HawkAI-Safety-Monitor"

# echo "🚀 Creating HawkAI with Vertex AI Agent Builder (Simpler Setup)"

# # Step 1: Set up authentication and enable APIs
# echo "🔐 Configuring authentication..."
# gcloud auth application-default set-quota-project $PROJECT_ID

# echo "📡 Enabling required APIs..."
# gcloud services enable \
#     aiplatform.googleapis.com \
#     dialogflow.googleapis.com \
#     discoveryengine.googleapis.com \
#     --project=$PROJECT_ID

# echo "⏰ Waiting for APIs to be fully enabled..."
# sleep 15

# # Step 2: Create Agent via REST API (since gcloud commands are limited)
# echo "🤖 Creating Vertex AI Agent..."

# # Create agent configuration
# cat > agent_config.json << EOF
# {
#   "displayName": "$AGENT_DISPLAY_NAME",
#   "defaultLanguageCode": "en",
#   "timeZone": "Asia/Kolkata",
#   "description": "HawkAI Safety Monitoring Agent for proactive event safety analysis",
#   "avatarUri": "",
#   "enableStackdriverLogging": true,
#   "enableSpellChecking": false,
#   "classification_threshold": 0.3,
#   "apiVersion": "API_VERSION_V3_BETA",
#   "tier": "TIER_STANDARD"
# }
# EOF

# # Get access token with proper quota project
# ACCESS_TOKEN=$(gcloud auth print-access-token)

# gcloud auth application-default print-access-token

# # Create the agent using REST API
# AGENT_RESPONSE=$(curl -s -X POST \
#   "https://dialogflow.googleapis.com/v3/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
#   -H "Authorization: Bearer ${ACCESS_TOKEN}" \
#   -H "Content-Type: application/json" \
#   -d @agent_config.json)

# # Extract agent name from response
# AGENT_NAME=$(echo "$AGENT_RESPONSE" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

# if [ -n "$AGENT_NAME" ]; then
#     echo "✅ Vertex AI Agent created: $AGENT_NAME"
#     AGENT_ID=$(basename "$AGENT_NAME")
# else
#     echo "❌ Failed to create agent. Response: $AGENT_RESPONSE"
#     echo ""
#     echo "🛠️  Manual Setup Required:"
#     echo "   1. Go to: https://console.cloud.google.com/vertex-ai/agents?project=$PROJECT_ID"
#     echo "   2. Click 'Create Agent'"
#     echo "   3. Configure with the following:"
#     echo "      - Name: HawkAI Safety Monitor" 
#     echo "      - Description: Safety monitoring for events"
#     echo "      - Language: English"
#     echo "      - Time Zone: Asia/Kolkata"
#     exit 1
# fi

# # Step 3: Create system instructions for the agent
# echo "🧠 Configuring Agent Instructions..."

# cat > system_instructions.json << EOF
# {
#   "instruction": "You are HawkAI, an advanced AI agent specialized in proactive event safety monitoring and emergency response analysis. Your primary role is to analyze safety situations, assess risks, and provide actionable recommendations for event organizers and safety personnel.

# CORE CAPABILITIES:
# - Crowd density analysis and capacity monitoring
# - Emergency response protocol guidance  
# - Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
# - Safety pattern analysis and anomaly detection
# - Real-time alert prioritization and escalation

# RESPONSE FORMAT:
# Always structure your responses as follows:
# 🛡️ SAFETY STATUS: [Risk Level] - [Key Concerns]
# 📊 ANALYSIS: [Current metrics and patterns]
# 🚨 ALERTS: [Priority level P1-P4, timeline, escalation needed]
# 💡 RECOMMENDATIONS: [2-3 specific actionable steps]

# SAFETY PRIORITY LEVELS:
# - P1 (Critical): Immediate life-threatening situations requiring instant response
# - P2 (High): Serious safety concerns requiring rapid response within 5-15 minutes
# - P3 (Medium): Moderate risks requiring attention within 30-60 minutes
# - P4 (Low): Preventive measures and routine monitoring

# Always prioritize human safety above all other considerations. Be concise but comprehensive, providing clear actionable guidance that event organizers can immediately implement."
# }
# EOF

# # Update agent with system instructions using REST API
# curl -s -X PATCH \
#   "https://dialogflow.googleapis.com/v3/${AGENT_NAME}" \
#   -H "Authorization: Bearer ${ACCESS_TOKEN}" \
#   -H "Content-Type: application/json" \
#   -d @system_instructions.json > /dev/null

# echo "✅ System instructions configured"

# # Step 4: Create training phrases for better NLU
# echo "🎯 Adding training examples..."

# # Create safety-related training phrases
# cat > training_phrases.json << EOF
# {
#   "trainingPhrases": [
#     {"parts": [{"text": "analyze crowd density at main stage"}]},
#     {"parts": [{"text": "emergency fire alarm triggered in west wing"}]},
#     {"parts": [{"text": "overcrowding detected at entrance gates"}]},
#     {"parts": [{"text": "medical emergency reported near food court"}]},
#     {"parts": [{"text": "weather alert - heavy rain expected"}]},
#     {"parts": [{"text": "security incident requiring immediate response"}]},
#     {"parts": [{"text": "check safety status of all venues"}]},
#     {"parts": [{"text": "evacuation procedures for 10000 attendees"}]},
#     {"parts": [{"text": "suspicious activity reported in parking area"}]},
#     {"parts": [{"text": "sound system failure causing panic"}]}
#   ]
# }
# EOF

# # Step 5: Test the agent
# echo "🧪 Testing Agent Response..."

# # Create test query
# cat > test_query.json << EOF
# {
#   "queryInput": {
#     "text": {
#       "text": "Emergency: Fire alarm triggered at main stage with 5000 people present. What should we do?",
#       "languageCode": "en"
#     }
#   },
#   "queryParams": {
#     "timeZone": "Asia/Kolkata"
#   }
# }
# EOF

# # Test the agent
# TEST_RESPONSE=$(curl -s -X POST \
#   "https://dialogflow.googleapis.com/v3/${AGENT_NAME}/sessions/test-session-123:detectIntent" \
#   -H "Authorization: Bearer ${ACCESS_TOKEN}" \
#   -H "Content-Type: application/json" \
#   -d @test_query.json)

# if echo "$TEST_RESPONSE" | grep -q "fulfillmentText\|responseMessages"; then
#     echo "✅ Agent responding correctly"
# else
#     echo "⚠️  Agent created but test failed - manual verification needed"
# fi

# # Cleanup temporary files
# rm -f agent_config.json system_instructions.json training_phrases.json test_query.json

# # Step 6: Generate integration code
# echo "📝 Generating integration code..."

# cat > hawkai_integration.py << 'EOF'
# import json
# from google.cloud import dialogflow_v3 as dialogflow

# class HawkAIAgent:
#     def __init__(self, project_id, location, agent_id):
#         self.project_id = project_id
#         self.location = location  
#         self.agent_id = agent_id
#         self.session_client = dialogflow.SessionsClient()
        
#     def detect_intent(self, session_id, text_input, language_code="en"):
#         """Send text to HawkAI agent and get response"""
#         session_path = self.session_client.session_path(
#             self.project_id, self.location, self.agent_id, session_id
#         )
        
#         text_input = dialogflow.TextInput(text=text_input, language_code=language_code)
#         query_input = dialogflow.QueryInput(text=text_input)
        
#         response = self.session_client.detect_intent(
#             request={"session": session_path, "query_input": query_input}
#         )
        
#         return response.query_result.response_messages[0].text.text[0]

# # Usage example:
# # agent = HawkAIAgent("hawkai-467107", "global", "YOUR_AGENT_ID")
# # response = agent.detect_intent("session-123", "Check crowd safety at venue A")
# # print(response)
# EOF

# echo "✅ Integration code created: hawkai_integration.py"

# # Final summary
# echo ""
# echo "🎉 HawkAI Vertex AI Agent Deployment Complete!"
# echo "=============================================="
# echo ""
# echo "✅ Project: $PROJECT_ID"
# echo "✅ Agent: $AGENT_DISPLAY_NAME"
# if [ -n "$AGENT_NAME" ]; then
#     echo "✅ Agent ID: $AGENT_ID"
#     echo "✅ Full Name: $AGENT_NAME"
# fi
# echo ""
# echo "🌐 Access your agent:"
# echo "   Console: https://console.cloud.google.com/vertex-ai/agents?project=$PROJECT_ID"
# echo "   Direct: https://console.cloud.google.com/vertex-ai/agents/$AGENT_ID?project=$PROJECT_ID"
# echo ""
# echo "🧪 Test Commands:"
# echo "   - 'Emergency: Fire at main entrance with 3000 people'"
# echo "   - 'Analyze crowd density - 8000 people in 5000 capacity venue'"
# echo "   - 'Medical emergency reported, need evacuation plan'"
# echo ""
# echo "📚 Integration:"
# echo "   - Use the generated hawkai_integration.py file"
# echo "   - Or integrate directly via REST API"
# echo "   - Web integration available through Agent Builder console"
# echo ""
# echo "🚀 HawkAI is ready for advanced safety monitoring!"

# # Display next steps
# echo ""
# echo "📋 Next Steps:"
# echo "1. Visit the console URL above to test your agent"
# echo "2. Use the built-in simulator to try safety scenarios"
# echo "3. Integrate using the hawkai_integration.py file" 
# echo "4. Deploy to production with your safety monitoring systems"