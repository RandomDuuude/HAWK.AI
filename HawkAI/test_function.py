#!/usr/bin/env python3

import requests
import json

# Test the deployed Cloud Function
FUNCTION_URL = "https://asia-south1-hawkai-467107.cloudfunctions.net/projecthawkai-handler"

def test_function():
    """Test the deployed ProjectHawkAi function"""
    
    test_cases = [
        {
            "name": "Crowd Safety Analysis",
            "payload": {
                "query": "Analyze crowd density at main stage - 5000 people in 3000 capacity venue with limited exits"
            }
        },
        {
            "name": "Emergency Alert",
            "payload": {
                "query": "Fire alarm in sector A and medical emergency near gate 3 - need immediate response"
            }
        },
        {
            "name": "Data Analytics",
            "payload": {
                "query": "Unusual pattern of incidents this week - 3x more medical emergencies than normal"
            }
        },
        {
            "name": "Weather Risk",
            "payload": {
                "query": "Heavy rain forecast with 30mph winds for outdoor event tomorrow"
            }
        }
    ]
    
    print("🧪 Testing ProjectHawkAi Cloud Function...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                FUNCTION_URL,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result['fulfillment_response']['messages'][0]['text']['text'][0]
                print(f"✅ Response: {message}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n🎯 Function URL for Vertex AI Agent Builder:")
    print(f"   {FUNCTION_URL}")

if __name__ == "__main__":
    test_function()