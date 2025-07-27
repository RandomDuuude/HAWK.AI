# Project constants for HawkAI

# Google Cloud configuration
PROJECT_ID = "hawkai-467107"
LOCATION = "asia-south1"

# Model configuration
MODEL_NAME_FLASH = "gemini-1.5-flash"
MODEL_NAME_PRO = "gemini-1.5-pro"
MODEL_NAME_FLASH_2 = "gemini-2.5-flash"

# Storage configuration
BUCKET_NAME = "hawkai-feedbucket"

# Function configuration
FUNCTION_NAME = "hawkai-handler"

# Set quota project to avoid authentication warnings
import os
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = PROJECT_ID