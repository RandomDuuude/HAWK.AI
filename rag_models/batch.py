from google.cloud import storage
import os

def upload_images_to_gcs(local_folder, gcs_folder):
    storage_client = storage.Client()
    bucket = storage_client.bucket("hawkai")

    for filename in os.listdir(local_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            blob = bucket.blob(f"{gcs_folder}/{filename}")
            blob.upload_from_filename(os.path.join(local_folder, filename))
            print(f"Uploaded {filename} to {gcs_folder}")

# Example usage
upload_images_to_gcs("/home/g/Google_Agentic_AI/images", "uploaded_images")
