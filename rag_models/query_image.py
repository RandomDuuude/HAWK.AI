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
similarity_threshold = 0.9999
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
    sim = cosine_similarity(input_embedding[:10], neighbor_embedding[:10])
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


# from vertexai.vision_models import Image as VertexImage
# from vertexai.vision_models import MultiModalEmbeddingModel
# from google.cloud import aiplatform
# import numpy as np
# import json

# # --- Step 1: Setup ---
# project = "hawkai-467107"
# location = "asia-south1"
# index_endpoint_name = "projects/181011797213/locations/asia-south1/indexEndpoints/8626381203437518848"
# deployed_index_id = "image_index"
# bucket_name = "hawkvision-feedback"

# # --- Step 2: Load image & embed ---
# image_path = "/home/g/Google_Agentic_AI/images/image_2.jpeg"
# image = VertexImage.load_from_file(image_path)
# embedding_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
# embedding_response = embedding_model.get_embeddings(image=image)
# embedding = embedding_response.image_embedding

# # --- Debug: Inspect embedding ---
# print("✅ Type of embedding:", type(embedding))
# print("✅ Length of embedding vector:", len(embedding))
# print("✅ First 10 values:", embedding[:10])
# print(f"✅ Embedding vector L2 norm: {np.linalg.norm(embedding):.4f}")

# embedding_json = {
#     "id": "debug_image",
#     "embedding": {
#         "values": list(embedding)
#     },
#     "metadata": {
#         "filename": image_path
#     }
# }
# print("✅ Example JSONL entry:\n", json.dumps(embedding_json, indent=2)[:1000])

# # --- Step 3: Init and Search in Index ---
# aiplatform.init(project=project, location=location)
# index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=index_endpoint_name)

# response = index_endpoint.find_neighbors(
#     deployed_index_id=deployed_index_id,
#     queries=[embedding],
#     num_neighbors=150,
# )

# print("Response", response)

# # --- Step 4: Process Results ---
# print("🔍 Searching for nearest neighbors...")
# if response and response[0].neighbors:
#     print("✅ Neighbors found:")
#     for i, neighbor in enumerate(response[0].neighbors[:5]):
#         print(f"{i+1}. ID: {neighbor.neighbor.resource_name} | Distance: {neighbor.distance:.4f}")
# else:
#     print("🚫 No neighbors found.")




# threshold = 0.3  # Adjust based on your similarity threshold

# if neighbors and neighbors[0].distance < threshold:
#     matched_id = neighbors[0].datapoint.datapoint_id
#     matched_image_gcs_uri = f"gs://{bucket_name}/{matched_id}.jpg"

#     print("✅ Match found:")
#     print(f"Matched ID: {matched_id}")
#     print(f"Matched Image URI: {matched_image_gcs_uri}")

#     # --- Step 5: Generate Explanation with Gemini ---
#     prompt = (
#         "Here is a query image and another image from the database that matches it closely.\n"
#         "Based on the visual content and context, describe what is happening in the matched image."
#     )

#     gemini = GenerativeModel("gemini-pro-vision")
#     gen_response = gemini.generate_content(
#         [
#             prompt,
#             Part.from_image(image),
#             Part.from_uri(matched_image_gcs_uri, mime_type="image/jpeg"),
#         ]
#     )

#     print("🎯 Gemini Answer:\n", gen_response.text)

# else:
#     print("❌ No match found in the index.")






# from vertexai.vision_models import Image as VertexImage
# from vertexai.vision_models import MultiModalEmbeddingModel
# from vertexai.preview.generative_models import GenerativeModel, Part
# from google.cloud import aiplatform

# # --- Step 1: Setup ---
# project = "hawkai-467107"
# location = "asia-south1"
# index_endpoint_name = "projects/181011797213/locations/asia-south1/indexEndpoints/5193512387474358272"

# # --- Step 2: Load image & embed ---
# image_path = "/home/g/Google_Agentic_AI/images/image_2.jpeg"
# image = VertexImage.load_from_file(image_path)
# model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
# response = model.get_embeddings(image=image)
# embedding = response.image_embedding

# # --- Step 3: Init and Search in Index ---
# aiplatform.init(project=project, location=location)

# index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name)

# response = index_endpoint.find_neighbors(
#     deployed_index_id="image_deployed_index",  # replace with your deployed index ID
#     queries=[embedding],
#     num_neighbors=1,
# )

# # --- Step 4: Check if match found ---
# # neighbors = response.nearest_neighbors[0].neighbors
# neighbors = response[0].neighbors
# threshold = 0.3  # Adjust based on your use case

# if neighbors and neighbors[0].distance < threshold:
#     matched_id = neighbors[0].datapoint.datapoint_id

#     # Construct GCS URI
#     matched_image_gcs_uri = f"gs://your-bucket-name/{matched_id}.jpg"  # Replace bucket name

#     print("✅ Match found:")
#     print(f"Matched ID: {matched_id}")
#     print(f"Matched Image URI: {matched_image_gcs_uri}")

#     # --- Step 5: Call Gemini ---
#     prompt = (
#         "Here is a query image and another image from the database that matches it closely.\n"
#         "Based on the visual content and context, describe what is happening in the matched image."
#     )

#     gemini = GenerativeModel("gemini-pro-vision")
#     response = gemini.generate_content(
#         [
#             prompt,
#             Part.from_image(image),
#             Part.from_uri(matched_image_gcs_uri, mime_type="image/jpeg"),
#         ]
#     )
#     print("🎯 Gemini Answer:\n", response.text)

# else:
#     print("❌ No match found in the index.")





# from vertexai.vision_models import Image as VertexImage
# from vertexai.vision_models import MultiModalEmbeddingModel
# from vertexai.language_models import TextGenerationModel
# # from vertexai.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint
# from vertexai.preview.generative_models import GenerativeModel, Part
# from PIL import Image
# import numpy as np
# from google.cloud import aiplatform

# # aiplatform.init(
# #     project="your-project-id",
# #     location="your-region"  # e.g., "us-central1"
# # )

# # index_endpoint = aiplatform.MatchingEngineIndexEndpoint("your-index-endpoint-id")


# # --- Step 1: Setup ---
# project = "hawkai-467107"
# location = "asia-south1" 
# index_endpoint_name = "projects/181011797213/locations/asia-south1/indexEndpoints/5193512387474358272"

# # --- Step 2: Load image & embed ---
# image_path = "/home/g/Google_Agentic_AI/images/image_2.jpeg"
# image = VertexImage.load_from_file(image_path)
# model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
# # embedding = model.get_embeddings(image=image).values
# response = model.get_embeddings(image=image)
# embedding = response.embedding

# # --- Step 3: Search in Index ---
# aiplatform.init(
#     project=project,
#     location=location  # e.g., "us-central1"
# )

# index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name)
# # index_endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=index_endpoint_name)

# response = index_endpoint.find_neighbors(
#     deployed_index_id="image_deployed_index",
#     queries=[embedding],
#     num_neighbors=1,
# )

# # --- Step 4: Check if match found ---
# neighbors = response.nearest_neighbors[0].neighbors
# threshold = 0.3  # Tune as needed

# if neighbors and neighbors[0].distance < threshold:
#     matched_id = neighbors[0].datapoint.datapoint_id

#     # --- Step 5: Get matched image from bucket ---
#     matched_image_gcs_uri = f"gs://your-bucket/{matched_id}.jpg"

#     print("✅ Match found:")
#     print(f"Matched ID: {matched_id}")
#     print(f"Matched Image URI: {matched_image_gcs_uri}")

#     # --- Step 6: Send both query image + matched image to Gemini with prompt ---
#     prompt = (
#         "Here is a query image and another image from the database that matches it closely.\n"
#         "Based on the visual content and context, describe what is happening in the matched image."
#     )

#     gemini = GenerativeModel("gemini-pro-vision")
#     response = gemini.generate_content(
#         [
#             prompt,
#             Part.from_image(image),  # query image
#             Part.from_uri(matched_image_gcs_uri, mime_type="image/jpeg")
#         ]
#     )
#     print("🎯 Gemini Answer:\n", response.text)

# else:
#     print("❌ No match found in the index.")
#     print("🔁 You can fall back to Gemini for direct analysis of the image if needed.")




# from vertexai.preview.language_models import ChatModel, InputOutputTextPair
# from vertexai.preview.vision_models import Image, ImageEmbeddingModel
# from vertexai.matching_engine import MatchingEngineIndexEndpoint
# from google.cloud import aiplatform
# import base64
# from PIL import Image as PILImage
# import io

# # Initialize Vertex AI
# aiplatform.init(project="hawkai-467107", location="asia-south1")

# # Load your index endpoint
# index_endpoint = MatchingEngineIndexEndpoint(
#     index_endpoint_name="projects/181011797213/locations/asia-south1/indexEndpoints/5193512387474358272"
# )

# # Load embedding model
# embedding_model = ImageEmbeddingModel.from_pretrained("imageembedding")

# # Load Gemini model for captioning / answering
# chat_model = ChatModel.from_pretrained("gemini-pro-vision")

# # Load your input image
# def load_image(image_path: str):
#     with open(image_path, "rb") as f:
#         return PILImage.open(io.BytesIO(f.read()))

# uploaded_image_path = "/home/g/Google_Agentic_AI/images/image_2.jpeg"
# uploaded_image = load_image(uploaded_image_path)

# # Generate embedding for uploaded image
# vertex_image = Image.from_pil_image(uploaded_image)
# embedding = embedding_model.get_embeddings(images=[vertex_image])[0].values

# # Search in Matching Engine
# response = index_endpoint.find_neighbors(
#     deployed_index_id="image_deployed_index",  # usually auto-generated or "default"
#     queries=[embedding],
#     num_neighbors=1
# )

# neighbors = response[0].neighbors
# threshold = 0.3

# if neighbors and neighbors[0].distance < threshold:
#     matched_id = neighbors[0].datapoint.datapoint_id
#     print("✅ Match found:", matched_id)

#     # Assume you have mapping from ID to image path
#     id_to_image_path = {
#         "img_01": "data/img_01.jpg",
#         "img_02": "data/img_02.jpg",
#         # Add your mappings...
#     }

#     matched_image_path = id_to_image_path.get(matched_id)

#     # Load matched image and ask Gemini a question like "What is this person doing?"
#     matched_image = load_image(matched_image_path)
#     vision_input = Image.from_pil_image(matched_image)

#     prompt = "What is this person doing?"
#     response = chat_model.predict(images=[vision_input], prompt=prompt)

#     print("🧠 Gemini Answer based on matched image:", response.text)

# else:
#     print("❌ No similar image found in index.")
