const express = require("express");
const { Storage } = require("@google-cloud/storage");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS
app.use(cors());

// Middleware to parse JSON with larger limit for base64 images
app.use(express.json({ 
  limit: '10mb' // Increased limit to handle base64 encoded images
}));

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  keyFilename: process.env.SERVICE_ACCOUNT_KEY_PATH,
});

const bucket = storage.bucket(process.env.GOOGLE_CLOUD_BUCKET_NAME);

// Helper function to convert base64 to buffer
function base64ToBuffer(base64String) {
  // Remove data URL prefix if present (e.g., "data:image/png;base64,")
  const base64Data = base64String.replace(/^data:image\/[a-z]+;base64,/, "");
  return Buffer.from(base64Data, 'base64');
}

// Helper function to detect image type from base64 string
function getImageTypeFromBase64(base64String) {
  if (base64String.startsWith('data:image/')) {
    const match = base64String.match(/data:image\/([a-zA-Z0-9]+);base64,/);
    return match ? match[1] : 'png';
  }
  return 'png'; // Default to PNG
}

// Base64 image upload endpoint
app.post("/upload-image", async (req, res) => {
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
    const baseFilename = filename ? filename.replace(/\.[^/.]+$/, "") : `image_${timestamp}`;
    const fileName = `uploaded_images/${timestamp}_${baseFilename}.png`;

    // Create file in bucket
    const file = bucket.file(fileName);

    // Upload the file as PNG
    await file.save(imageBuffer, {
      metadata: {
        contentType: 'image/png',
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
      convertedType: 'png',
    });

    console.log(`✅ Image uploaded: ${fileName} (converted from ${originalImageType} to PNG)`);
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
  res.json({ status: "Server is running!" });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error("Global error handler:", error);
  res.status(500).json({
    success: false,
    error: error.message || "Internal server error",
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📤 Upload endpoint: POST http://localhost:${PORT}/upload-image`);
  console.log(`📋 Expected request body format:`);
  console.log(`   {`);
  console.log(`     "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",`);
  console.log(`     "filename": "optional-custom-name" (optional)`);
  console.log(`   }`);
});