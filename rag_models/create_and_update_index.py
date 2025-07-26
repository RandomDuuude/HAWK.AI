import os
import json
import vertexai
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image
from google.cloud import storage, aiplatform

# ---- Config ----
PROJECT = "hawkai-467107"
LOCATION = "asia-south1"
BUCKET_NAME = "hawkvision-feedback"
IMAGE_FOLDER = "uploaded_images"
JSONL_FILE = "image_embeddings.jsonl"
GCS_JSONL_PATH = f"gs://{BUCKET_NAME}/{JSONL_FILE}"
INDEX_DISPLAY_NAME = "image-index-fixed"
EMBEDDING_DIMENSION = 1408  # MultimodalEmbedding model output

# ---- Init ----
vertexai.init(project=PROJECT, location=LOCATION)
aiplatform.init(project=PROJECT, location=LOCATION)
model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# ---- Step 1: Extract Embeddings from GCS ----
def extract_embedding_from_gcs(gcs_path: str):
    blob_path = gcs_path.replace(f"gs://{BUCKET_NAME}/", "")
    blob = bucket.blob(blob_path)
    image_bytes = blob.download_as_bytes()
    image = Image(image_bytes=image_bytes)
    response = model.get_embeddings(image=image)
    return response.image_embedding

def extract_embeddings_and_write_jsonl():
    jsonl_lines = []
    image_count = 0

    for blob in storage_client.list_blobs(BUCKET_NAME, prefix=IMAGE_FOLDER):
        if not blob.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        gcs_uri = f"gs://{BUCKET_NAME}/{blob.name}"
        try:
            print(f"🔄 Processing: {gcs_uri}")
            embedding = extract_embedding_from_gcs(gcs_uri)

            if embedding and len(embedding) == EMBEDDING_DIMENSION:
                json_obj = {
                    "id": os.path.basename(blob.name),
                    "embedding": embedding,  # Must be a flat list!
                    "metadata": {"gcs_path": gcs_uri}
                }
                jsonl_lines.append(json.dumps(json_obj))
                image_count += 1
            else:
                print(f"⚠️ Skipped: Invalid or empty embedding for {blob.name}")

        except Exception as e:
            print(f"❌ Error processing {blob.name}: {e}")

    if image_count == 0:
        raise RuntimeError("❌ No valid embeddings found. JSONL will not be created.")

    with open(JSONL_FILE, "w") as f:
        f.write("\n".join(jsonl_lines))

    print(f"✅ Saved {image_count} embeddings to {JSONL_FILE}")

# ---- Step 2: Upload JSONL to GCS ----
def upload_jsonl_to_gcs():
    blob = bucket.blob(JSONL_FILE)
    blob.upload_from_filename(JSONL_FILE)
    print(f"✅ Uploaded {JSONL_FILE} to {GCS_JSONL_PATH}")

# ---- Step 3: Create Index ----
def create_index():
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=INDEX_DISPLAY_NAME,
        contents_delta_uri=GCS_JSONL_PATH,
        dimensions=EMBEDDING_DIMENSION,
        approximate_neighbors_count=150,
        distance_measure_type="DOT_PRODUCT_DISTANCE"
    )
    print(f"✅ Created Matching Engine Index: {index.resource_name}")

# ---- Run Everything ----
if __name__ == "__main__":
    extract_embeddings_and_write_jsonl()
    upload_jsonl_to_gcs()
    create_index()
















# import vertexai
# from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image
# from google.cloud import storage, aiplatform
# import json
# import os

# # ---- Config ----
# PROJECT = "hawkai-467107"
# LOCATION = "asia-south1"
# BUCKET_NAME = "hawkvision-feedback"
# IMAGE_FOLDER = "uploaded_images"
# JSONL_FILE = "image_embeddings.jsonl"
# GCS_JSONL_PATH = f"gs://{BUCKET_NAME}/{JSONL_FILE}"
# INDEX_DISPLAY_NAME = "image-index"
# EMBEDDING_DIMENSION = 1408  # As per multimodalembedding model

# # ---- Init Vertex AI ----
# vertexai.init(project=PROJECT, location=LOCATION)
# aiplatform.init(project=PROJECT, location=LOCATION)
# model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
# storage_client = storage.Client()
# bucket = storage_client.bucket(BUCKET_NAME)

# # ---- Extract Embeddings and Write JSONL ----
# def extract_embedding_from_gcs(gcs_path: str):
#     blob_path = gcs_path.replace(f"gs://{BUCKET_NAME}/", "")
#     blob = bucket.blob(blob_path)
#     image_bytes = blob.download_as_bytes()
#     image = Image(image_bytes=image_bytes)
#     return model.get_embeddings(image=image).image_embedding

# def extract_embeddings_and_write_jsonl():
#     jsonl_lines = []
#     for blob in storage_client.list_blobs(BUCKET_NAME, prefix=IMAGE_FOLDER):
#         if blob.name.lower().endswith((".jpg", ".jpeg", ".png")):
#             gcs_uri = f"gs://{BUCKET_NAME}/{blob.name}"
#             print(f"Processing: {gcs_uri}")
#             embedding = extract_embedding_from_gcs(gcs_uri)
#             json_obj = {
#                 "id": blob.name,
#                 "embedding": {"values": embedding},
#                 "metadata": {"gcs_path": gcs_uri}
#             }
#             jsonl_lines.append(json.dumps(json_obj))

#     with open(JSONL_FILE, "w") as f:
#         f.write("\n".join(jsonl_lines))

#     print(f"✅ Saved embeddings to {JSONL_FILE}")

# # ---- Upload JSONL to GCS ----
# def upload_jsonl_to_gcs():
#     blob = bucket.blob(JSONL_FILE)
#     blob.upload_from_filename(JSONL_FILE)
#     print(f"✅ Uploaded {JSONL_FILE} to {GCS_JSONL_PATH}")

# # ---- Create or Update Index ----
# def create_index():
#     from google.cloud.aiplatform.matching_engine import MatchingEngineIndex, MatchingEngineIndexEndpoint

#     index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
#         display_name=INDEX_DISPLAY_NAME,
#         contents_delta_uri=GCS_JSONL_PATH,
#         dimensions=EMBEDDING_DIMENSION,
#         approximate_neighbors_count=150,
#         distance_measure_type="DOT_PRODUCT_DISTANCE"
#     )
#     print(f"✅ Created Matching Engine Index: {index.resource_name}")

# # ---- Run All ----
# if __name__ == "__main__":
#     extract_embeddings_and_write_jsonl()
#     upload_jsonl_to_gcs()
#     create_index()
