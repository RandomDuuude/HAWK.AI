# Image Upload Server

A Node.js Express server for uploading images to Google Cloud Storage with Firebase integration.

## Features

- ✅ Upload single or multiple images
- ✅ Automatic file validation and sanitization
- ✅ Google Cloud Storage integration
- ✅ Public URL generation
- ✅ Image management (get, delete, list)
- ✅ Error handling and logging
- ✅ Environment-based configuration
- ✅ CORS support
- ✅ Development and production ready

## Project Structure

```
image-upload-server/
├── config/
│   ├── storage.js              # Google Cloud Storage configuration
│   └── serviceAccountKey.json  # Firebase service account key (add this)
├── middleware/
│   ├── upload.js              # Multer upload configuration
│   └── errorHandler.js        # Error handling middleware
├── routes/
│   ├── upload.js              # Upload endpoints
│   └── images.js              # Image management endpoints
├── utils/
│   └── fileUtils.js           # File utility functions
├── .env                       # Environment variables (create this)
├── .gitignore                 # Git ignore file
├── package.json               # Dependencies and scripts
├── server.js                  # Main server file
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy `.env` file and update with your Firebase project details:
```bash
# Update these values in .env
GOOGLE_CLOUD_PROJECT_ID=your-firebase-project-id
GOOGLE_CLOUD_BUCKET_NAME=your-firebase-project-id.appspot.com
```

### 3. Add Firebase Service Account Key
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save as `config/serviceAccountKey.json`

### 4. Run the Server
```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

## API Endpoints

### Upload Endpoints
- `POST /api/upload-image` - Upload single image
- `POST /api/upload-images` - Upload multiple images (max 5)

### Image Management
- `GET /api/image/:fileName` - Get image info
- `DELETE /api/image/:fileName` - Delete image
- `GET /api/images` - List all images

### Utility
- `GET /health` - Health check
- `GET /` - API documentation

## Usage Examples

### Upload Single Image
```bash
curl -X POST \
  -F "image=@path/to/your/image.jpg" \
  http://localhost:3000/api/upload-image
```

### Upload Multiple Images
```bash
curl -X POST \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  http://localhost:3000/api/upload-images
```

### Get Image Info
```bash
curl http://localhost:3000/api/image/your-filename.jpg
```

### Delete Image
```bash
curl -X DELETE http://localhost:3000/api/image/your-filename.jpg
```

## Configuration

### Environment Variables
- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)
- `GOOGLE_CLOUD_PROJECT_ID` - Your Firebase project ID
- `GOOGLE_CLOUD_BUCKET_NAME` - Your storage bucket name
- `SERVICE_ACCOUNT_KEY_PATH` - Path to service account key
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 5MB)
- `ALLOWED_FILE_TYPES` - Comma-separated list of allowed MIME types

### File Upload Limits
- Maximum file size: 5MB (configurable)
- Allowed types: JPEG, JPG, PNG, GIF, WebP
- Maximum files per request: 5 (for multiple upload)

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "data": {
    "fileName": "images/1690123456_789_photo.jpg",
    "originalName": "photo.jpg",
    "publicUrl": "https://storage.googleapis.com/...",
    "size": 245760,
    "formattedSize": "240 KB",
    "mimetype": "image/jpeg",
    "uploadedAt": "2023-07-23T10:30:56.789Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "File too large",
  "message": "Maximum file size is 5MB",
  "code": "FILE_TOO_LARGE"
}
```

## Development

### Scripts
- `npm start` - Start production server
- `npm run dev` - Start development server with auto-restart

### Adding New Features
1. Create new routes in `routes/` directory
2. Add middleware in `middleware/` directory
3. Add utilities in `utils/` directory
4. Update main server file to include new routes

## Security Notes

- Never commit `serviceAccountKey.json` to version control
- Use environment variables for sensitive configuration
- Implement rate limiting for production use
- Consider adding authentication middleware
- Validate and sanitize all user inputs

## Troubleshooting

### Common Issues
1. **Service account key not found**: Make sure `config/serviceAccountKey.json` exists
2. **Bucket access denied**: Verify your Firebase project ID and bucket name
3. **File upload fails**: Check file size and type restrictions
4. **CORS errors**: Ensure CORS is properly configured for your frontend domain

### Logs
The server logs all important operations and errors to the console.

## License

MIT License - feel free to use this project for your applications!
