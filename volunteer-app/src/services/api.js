// src/services/api.js
import axios from "axios";

const BACKEND_URL =
  "https://us-central1-hawkai-e3970.cloudfunctions.net/api/upload-image"; // Not needed for mock

export const uploadImageToServer = async (base64, filename) => {
  const payload = {
    image: base64,
    filename: filename,
  };

  const response = await axios.post(BACKEND_URL, payload, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

export async function sendLostFoundQuery(name, file) {
  console.log(`[Mock] Searching for person: ${name}`);
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate delay
  return {
    name,
    imageUrl: "https://via.placeholder.com/200x200.png?text=Found+Person",
  };
}
