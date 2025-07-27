# HawkAI Configuration

This directory contains configuration files for the HawkAI project.

## Constants

The `constants.py` file contains project-wide constants that are used across the codebase. This centralized approach makes it easier to manage configuration values and ensures consistency across the project.

### Available Constants

- `PROJECT_ID`: Google Cloud project ID
- `LOCATION`: Google Cloud region
- `MODEL_NAME_FLASH`: Gemini Flash model name
- `MODEL_NAME_PRO`: Gemini Pro model name
- `BUCKET_NAME`: Google Cloud Storage bucket name
- `FUNCTION_NAME`: Cloud Function name

### Usage

#### In Python Files

```python
# Import specific constants
from config.constants import PROJECT_ID, LOCATION

# Or import all constants
from config import constants
```

#### In Shell Scripts

Use the `scripts/extract_constants.py` script to extract constants for use in shell scripts:

```bash
# Source constants directly
eval "$(python3 ./scripts/extract_constants.py)"

# Now you can use the constants in your script
echo "Project ID: $PROJECT_ID"
echo "Location: $LOCATION"
```