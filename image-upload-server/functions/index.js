/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {setGlobalOptions} = require("firebase-functions");
const {onRequest} = require("firebase-functions/https");
const logger = require("firebase-functions/logger");
const express = require("express");
const cors = require("cors");
const { Storage } = require("@google-cloud/storage");
// Check required environment variables
const requiredEnv = ["GOOGLE_CLOUD_PROJECT_ID", "GOOGLE_CLOUD_BUCKET_NAME", "SERVICE_ACCOUNT_KEY_PATH"];
for (const key of requiredEnv) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  keyFilename: process.env.SERVICE_ACCOUNT_KEY_PATH,
});
const bucket = storage.bucket(process.env.GOOGLE_CLOUD_BUCKET_NAME);

function base64ToBuffer(base64String) {
  const base64Data = base64String.replace(/^data:image\/[a-z]+;base64,/, "");
  return Buffer.from(base64Data, 'base64');
}

function getImageTypeFromBase64(base64String) {
  if (base64String.startsWith('data:image/')) {
    const match = base64String.match(/data:image\/([a-zA-Z0-9]+);base64,/);
    return match ? match[1] : 'png';
  }
  return 'png';
}

app.post("/upload-image", async (req, res) => {
  try {
    const { image, filename } = req.body;
    if (!image) {
      return res.status(400).json({ success: false, error: "No base64 image data provided" });
    }
    let imageBuffer;
    try {
      imageBuffer = base64ToBuffer(image);
    } catch (error) {
      return res.status(400).json({ success: false, error: "Invalid base64 image data" });
    }
    if (imageBuffer.length > 5 * 1024 * 1024) {
      return res.status(400).json({ success: false, error: "File too large. Maximum size is 5MB." });
    }
    const originalImageType = getImageTypeFromBase64(image);
    const timestamp = Date.now();
    const baseFilename = filename ? filename.replace(/\.[^/.]+$/, "") : `image_${timestamp}`;
    const fileName = `uploaded_images/${timestamp}_${baseFilename}.png`;
    const file = bucket.file(fileName);
    await file.save(imageBuffer, { metadata: { contentType: 'image/png' } });
    await file.makePublic();
    const publicUrl = `https://storage.googleapis.com/${bucket.name}/${fileName}`;
    res.json({ success: true, message: "Image uploaded successfully", fileName, publicUrl, size: imageBuffer.length, originalType: originalImageType, convertedType: 'png' });
  } catch (error) {
    res.status(500).json({ success: false, error: "Failed to upload image", message: error.message });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "Server is running!" });
});

exports.api = onRequest(app);
setGlobalOptions({ maxInstances: 10 });

// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });
