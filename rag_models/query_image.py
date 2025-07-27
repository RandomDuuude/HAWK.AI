from vertexai.vision_models import Image as VertexImage
from vertexai.vision_models import MultiModalEmbeddingModel
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai import init as vertexai_init  # <-- Init Vertex AI in correct region
from google.cloud import storage
import numpy as np
import json

# --- Config ---
project = "hawkai-467107"
location_gemini = "us-central1"  # Required for Gemini
bucket_name = "hawkvision-feedback"
jsonl_blob_path = "image_embeddings.jsonl"
image_path = "/home/g/Google_Agentic_AI/images/image_2.jpeg"
similarity_threshold = 0.2
custom_prompt = "Give me insights based on the image."

# --- Step 1: Load image and get embedding ---
image = VertexImage.load_from_file(image_path)
embedding_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
embedding_response = embedding_model.get_embeddings(image=image)
input_embedding = embedding_response.image_embedding
print("✅ First 10 values of input embedding:", input_embedding[:10])

# --- Step 2: Load all embeddings from GCS and compare ---
print("📥 Reading JSONL from GCS...")
storage_client = storage.Client(project=project)
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(jsonl_blob_path)
content = blob.download_as_text()

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print("🔍 Comparing input embedding to JSONL embeddings...")
match_found = False
for line in content.strip().splitlines():
    data = json.loads(line)
    neighbor_embedding = data["embedding"]
    sim = cosine_similarity(input_embedding, neighbor_embedding)
    if sim >= similarity_threshold:
        print(f"✅ Match found! ID: {data['id']} | Similarity: {sim:.4f}")
        match_found = True
        break

# --- Step 3: If matched, send image and prompt to Gemini ---
if match_found:
    print("🧠 Sending image and prompt to Gemini...")
    
    # Gemini only works in us-central1
    vertexai_init(project=project, location=location_gemini)
    gemini = GenerativeModel("gemini-2.5-flash")

    with open(image_path, "rb") as img_file:
        image_part = Part.from_data(data=img_file.read(), mime_type="image/jpeg")

    response = gemini.generate_content([
        image_part,
        custom_prompt
    ])

    print("🧠 Gemini Response:\n", response.text)
else:
    print("🚫 No similar embedding found — skipping Gemini.")
