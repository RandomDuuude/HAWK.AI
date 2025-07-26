const express = require("express");
const multer = require("multer");
const { Storage } = require("@google-cloud/storage");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS
app.use(cors());

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  keyFilename: process.env.SERVICE_ACCOUNT_KEY_PATH,
});

const bucket = storage.bucket(process.env.GOOGLE_CLOUD_BUCKET_NAME);

// Configure multer for memory storage
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith("image/")) {
      cb(null, true);
    } else {
      cb(new Error("Only image files are allowed!"), false);
    }
  },
});

// Single image upload endpoint
app.post("/upload-image", upload.single("image"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: "No image file provided",
      });
    }

    // Generate unique filename
    const timestamp = Date.now();
    const fileName = `images/${timestamp}_${req.file.originalname}`;

    // Create file in bucket
    const file = bucket.file(fileName);

    // Upload the file
    await file.save(req.file.buffer, {
      metadata: {
        contentType: req.file.mimetype,
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
      size: req.file.size,
      mimetype: req.file.mimetype,
    });

    console.log(`✅ Image uploaded: ${fileName}`);
  } catch (error) {
    console.error("Upload error:", error);
    res.status(500).json({
      success: false,
      error: "Failed to upload image",
      message: error.message,
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error.code === "LIMIT_FILE_SIZE") {
    return res.status(400).json({
      success: false,
      error: "File too large. Maximum size is 5MB.",
    });
  }

  if (error.message === "Only image files are allowed!") {
    return res.status(400).json({
      success: false,
      error: "Only image files are allowed",
    });
  }

  res.status(500).json({
    success: false,
    error: error.message,
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📤 Upload endpoint: POST http://localhost:${PORT}/upload-image`);
});
