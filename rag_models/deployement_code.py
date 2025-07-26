from google.cloud import aiplatform

# Initialize AI Platform
aiplatform.init(project='hawkai-467107', location='asia-south1')

# Replace with your actual index ID
INDEX_ID = '2591592887133143040'

# Step 1: Create Index Endpoint
index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name='image-matching-endpoint',
    description='Endpoint for image vector search',
    public_endpoint_enabled=True  # Set to False if you want it private
)
print(f"✅ Created Index Endpoint: {index_endpoint.resource_name}")

# Step 2: Deploy Index to Endpoint
deployed_index = index_endpoint.deploy_index(
    index=aiplatform.MatchingEngineIndex(INDEX_ID),
    deployed_index_id='image_index',
    machine_type='n1-standard-16',  # You can change this if needed
)
print("✅ Index deployed successfully to endpoint.")
print(f"🧠 You can now query using this endpoint: {index_endpoint.resource_name}")
