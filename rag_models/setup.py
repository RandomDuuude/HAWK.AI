from google.cloud import aiplatform
from google.cloud import storage
import os


PROJECT_ID = "hawkai-467107"
LOCATION = "asia-south1" 
BUCKET_NAME = "hawkvision-feedback"

aiplatform.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_NAME)


# from google.cloud import storage
# import os

def upload_images_to_gcs(local_folder, gcs_folder):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    for filename in os.listdir(local_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            blob = bucket.blob(f"{gcs_folder}/{filename}")
            blob.upload_from_filename(os.path.join(local_folder, filename))
            print(f"Uploaded {filename} to {gcs_folder}")

# Example usage
upload_images_to_gcs("/home/g/Google_Agentic_AI/images", "uploaded_images")
