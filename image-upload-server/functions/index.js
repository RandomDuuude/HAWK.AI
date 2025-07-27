// functions/index.js
const functions = require("firebase-functions");
const express = require("express");
const { Storage } = require("@google-cloud/storage");
const cors = require("cors");

const app = express();

// Enable CORS
app.use(cors({ origin: true }));

// Middleware to parse JSON with larger limit for base64 images
app.use(
  express.json({
    limit: "10mb", // Increased limit to handle base64 encoded images
  })
);

// Initialize Google Cloud Storage
const storage = new Storage();

// Get bucket name from Firebase config
const config = functions.config();
const bucketName =
  config.storage?.bucket_name ||
  config.google?.bucket_name ||
  `${process.env.GCLOUD_PROJECT}.appspot.com`;
const bucket = storage.bucket(bucketName);

// Helper function to convert base64 to buffer
function base64ToBuffer(base64String) {
  // Remove data URL prefix if present (e.g., "data:image/png;base64,")
  const base64Data = base64String.replace(/^data:image\/[a-z]+;base64,/, "");
  return Buffer.from(base64Data, "base64");
}

// Helper function to detect image type from base64 string
function getImageTypeFromBase64(base64String) {
  if (base64String.startsWith("data:image/")) {
    const match = base64String.match(/data:image\/([a-zA-Z0-9]+);base64,/);
    return match ? match[1] : "png";
  }
  return "png"; // Default to PNG
}

// Base64 image upload endpoint
app.post("/upload-images", async (req, res) => {
  try {
    const { image, filename } = req.body;

    // Validate required fields
    if (!image) {
      return res.status(400).json({
        success: false,
        error: "No base64 image data provided",
      });
    }

    // Convert base64 to buffer
    let imageBuffer;
    try {
      imageBuffer = base64ToBuffer(image);
    } catch (error) {
      return res.status(400).json({
        success: false,
        error: "Invalid base64 image data",
      });
    }

    // Check file size (5MB limit)
    if (imageBuffer.length > 5 * 1024 * 1024) {
      return res.status(400).json({
        success: false,
        error: "File too large. Maximum size is 5MB.",
      });
    }

    // Detect original image type
    const originalImageType = getImageTypeFromBase64(image);

    // Generate unique filename with PNG extension
    const timestamp = Date.now();
    const baseFilename = filename
      ? filename.replace(/\.[^/.]+$/, "")
      : `image_${timestamp}`;
    const fileName = `uploaded_images/${timestamp}_${baseFilename}.png`;

    // Create file in bucket
    const file = bucket.file(fileName);

    // Upload the file as PNG
    await file.save(imageBuffer, {
      metadata: {
        contentType: "image/png",
      },
    });

    // Make file public
    await file.makePublic();

    // Get public URL
    const publicUrl = `https://storage.googleapis.com/${bucket.name}/${fileName}`;

    // Send success response
    res.json({
      success: true,
      message: "Image uploaded successfully",
      fileName: fileName,
      publicUrl: publicUrl,
      size: imageBuffer.length,
      originalType: originalImageType,
      convertedType: "png",
    });

    console.log(
      `✅ Image uploaded: ${fileName} (converted from ${originalImageType} to PNG)`
    );
  } catch (error) {
    console.error("Upload error:", error);
    res.status(500).json({
      success: false,
      error: "Failed to upload image",
      message: error.message,
    });
  }
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "Server is running on Firebase!",
    bucketName: bucketName, // Add this to debug bucket name
    projectId: process.env.GCLOUD_PROJECT,
  });
});

// Root endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Image Upload API",
    endpoints: {
      health: "GET /health",
      upload: "POST /upload-images",
    },
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error("Global error handler:", error);
  res.status(500).json({
    success: false,
    error: error.message || "Internal server error",
  });
});

// Export the Express app as a Firebase Function
exports.api = functions
  .runWith({
    memory: "1GB", // Increased memory for image processing
    timeoutSeconds: 300, // 5 minutes timeout for large uploads
  })
  .https.onRequest(app);
