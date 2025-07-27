#!/bin/bash

# HawkAI Deployment Script - Optimized for Speed

# Source constants from Python script
eval "$(python3 ./scripts/extract_constants.py)"

# Verify constants were loaded
if [ -z "$PROJECT_ID" ] || [ -z "$LOCATION" ] || [ -z "$FUNCTION_NAME" ]; then
  echo "❌ Error: Failed to load constants from config/constants.py"
  exit 1
fi

echo "🚀 Deploying HawkAI to Vertex AI Agent Builder..."

# Step 1: Enable required APIs in parallel
echo "📡 Enabling APIs in parallel..."
gcloud services enable dialogflow.googleapis.com cloudfunctions.googleapis.com run.googleapis.com aiplatform.googleapis.com --project=$PROJECT_ID

# Step 2: Create optimized .gcloudignore to exclude unnecessary files
echo "🗂️  Creating .gcloudignore..."
cat > .gcloudignore << EOF
.git/
.pytest_cache/
__pycache__/
*.pyc
*.pyo
*.pyd
.DS_Store
.vscode/
.idea/
*.log
test_*
*_test.py
README.md
.gitignore
venv/
env/
node_modules/
*.zip
*.tar.gz
EOF

# Step 3: Create minimal requirements.txt for faster deployment
echo "📦 Creating minimal requirements.txt..."
cat > requirements.txt << EOF
functions-framework==3.8.1
vertexai==1.60.0
google-cloud-logging==3.8.0
EOF

# Step 4: Deploy Cloud Function with optimized settings
echo "☁️  Deploying Cloud Function with optimized settings..."

# Check if function exists to determine if this is an update
FUNCTION_EXISTS=$(gcloud functions describe $FUNCTION_NAME --region=$LOCATION --project=$PROJECT_ID --format="value(name)" 2>/dev/null)

if [ -n "$FUNCTION_EXISTS" ]; then
    echo "📝 Updating existing function (faster than new deployment)..."
else
    echo "🆕 Creating new function..."
fi

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime python311 \
    --trigger-http \
    --entry-point projectHawkAI_handler \
    --memory 512MiB \
    --timeout 60s \
    --max-instances 10 \
    --min-instances 0 \
    --region $LOCATION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_QUOTA_PROJECT=$PROJECT_ID" \
    --source=. \
    --quiet

# Step 5: Get function URL and validate deployment
echo "🔍 Validating deployment..."
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$LOCATION --project=$PROJECT_ID --format="value(serviceConfig.uri)" 2>/dev/null)

if [ -z "$FUNCTION_URL" ]; then
    echo "❌ Deployment failed - function URL not found"
    exit 1
fi

# Quick health check
echo "🏥 Performing health check..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FUNCTION_URL" || echo "000")
if [ "$HTTP_STATUS" -eq "200" ] || [ "$HTTP_STATUS" -eq "405" ]; then
    echo "✅ Function is responding correctly"
else
    echo "⚠️  Function deployed but health check returned status: $HTTP_STATUS"
fi

echo "✅ Cloud Function deployed successfully!"
echo "🔗 Function URL: $FUNCTION_URL"

# Cleanup temporary files
echo "🧹 Cleaning up..."
# rm -f requirements.txt .gcloudignore  # Uncomment if you want to remove these files

# Step 6: Performance tips and next steps
echo ""
echo "⚡ Performance Tips Applied:"
echo "=========================="
echo "• APIs enabled in parallel"
echo "• Minimal dependencies (only 3 packages)"
echo "• Reduced memory allocation (512MiB)"
echo "• .gcloudignore excludes unnecessary files"
echo "• Used --quiet flag for faster deployment"
echo "• Health check validates deployment"
echo ""
echo "📋 Next Steps - Manual Configuration in Vertex AI Agent Builder:"
echo "=============================================================="
echo ""
echo "1. Go to Vertex AI Agent Builder Console:"
echo "   https://console.cloud.google.com/vertex-ai/agents?project=$PROJECT_ID"
echo ""
echo "2. Click 'Create Agent' and configure:"
echo "   - Name: HawkAI Safety Monitor"
echo "   - Description: Multi-agent system for proactive event safety monitoring"
echo "   - Region: $LOCATION"
echo "   - Language: English (en)"
echo ""
echo "3. In Agent Settings, set webhook URL:"
echo "   $FUNCTION_URL"
echo ""
echo "4. Create these intents:"
echo "   - safety.crowd.analysis (for crowd safety queries)"
echo "   - analytics.pattern.analysis (for data analysis queries)"
echo "   - alert.emergency.management (for emergency alerts)"
echo ""
echo "5. Test phrases for each intent:"
echo "   Safety: 'analyze crowd density', 'check venue safety', 'overcrowding'"
echo "   Analytics: 'historical patterns', 'detect anomalies', 'trend analysis'"  
echo "   Alerts: 'emergency alert', 'fire alarm', 'medical emergency'"
echo ""
echo "6. Enable 'Use webhook for all intents' in fulfillment settings"
echo ""
echo "🎯 After setup, test your agent in the Agent Builder console!"
echo "💬 You'll have a full chat UI to interact with HawkAI!"

# Optional: Display deployment time
echo ""
echo "⏱️  Deployment completed at: $(date)"
echo "🚀 Ready to configure in Vertex AI Agent Builder!"