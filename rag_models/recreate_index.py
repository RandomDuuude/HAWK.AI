from google.cloud import aiplatform
import json

# --- Step 1: Setup ---
project = "hawkai-467107"
location = "asia-south1"
index_id = "2591592887133143040"

aiplatform.init(project=project, location=location)

# --- Step 2: Load embeddings from JSONL ---
datapoints = []

with open("image_embeddings.jsonl", "r") as f:
    for line in f:
        if line.strip():
            embedding_data = json.loads(line)
            datapoint = aiplatform.MatchingEngineIndexDatapoint(
                datapoint_id=embedding_data["id"],
                feature_vector=embedding_data["embedding"]["values"],
                restricts=None,
                crowding_tag=None,
                metadata=embedding_data.get("metadata", {})
            )
            datapoints.append(datapoint)

print(f"📦 Loaded {len(datapoints)} datapoints.")

# --- Step 3: Upsert into index ---
index = aiplatform.MatchingEngineIndex(index_name=index_id)
index.upsert_datapoints(datapoints=datapoints)
print("✅ Successfully upserted datapoints.")
