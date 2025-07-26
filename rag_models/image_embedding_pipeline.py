from vertexai.preview.vision_models import MultiModalEmbeddingModel
from vertexai.preview.vision_models import Image
from google.cloud import storage
import vertexai

# Initialize Vertex AI
vertexai.init(project="hawkai-467107", location="asia-south1")

# Load the model
model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

# GCS bucket details
BUCKET_NAME = "hawkai-feedbucket"
FOLDER = "uploaded_images"

# Initialize GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# Function to extract embedding from GCS path
def extract_embedding_from_gcs(gcs_path: str):
    blob_path = gcs_path.replace(f"gs://{BUCKET_NAME}/", "")
    blob = bucket.blob(blob_path)
    image_bytes = blob.download_as_bytes()
    
    image = Image(image_bytes=image_bytes)
    embeddings = model.get_embeddings(image=image)
    return embeddings.image_embedding  # ✅ FIXED here

# Extract embeddings for all images in folder
image_embeddings = []
for blob in storage_client.list_blobs(BUCKET_NAME, prefix=FOLDER):
    if blob.name.lower().endswith((".jpg", ".jpeg", ".png")):
        gcs_uri = f"gs://{BUCKET_NAME}/{blob.name}"
        embedding = extract_embedding_from_gcs(gcs_uri)
        image_embeddings.append({
            "id": blob.name,
            "embedding": embedding,
            "gcs_path": gcs_uri
    "embedding": {"values": embedding},
    "metadata": {"gcs_path": gcs_uri}
        })

print(f"Extracted embeddings for {len(image_embeddings)} images.")
