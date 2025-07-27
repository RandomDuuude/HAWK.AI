# 🦅 HAWK.AI

**HAWK.AI** is a modular, multi-agent AI system designed to monitor, analyze, and respond to crowd-based scenarios in real-time.  
It integrates:
- A **Python backend** with agent-based coordination,
- A **React-based web frontend** for interaction and visualization,
- A **Node.js-based upload server** for secure image handling.

---

## 📦 Project Structure

```
HAWK.AI-main/
├── HawkAI/                 # Core Python-based AI logic and agents
│   ├── agents/             # Modular AI agents (analytics, alert, safety)
│   ├── config/             # Configuration constants and agent setup
│   ├── deployment/         # Deployment scripts (Vertex AI)
│   ├── scripts/            # Utility/test scripts
│   ├── main.py             # Main entry point for system execution
│   ├── fast-main.py        # Fast startup script
│   └── requirements.txt    # Python dependencies
├── hawkai-chat/            # React-based frontend app
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
├── image-upload-server/    # Node.js-based image upload and storage service
│   ├── index.js
│   ├── package.json
│   └── firebase.json
└── README.md               # Root project documentation
```

---

## 🧠 Core Features

- **Multi-Agent AI System** with modular components:
  - `AlertAgent` – Detects anomalies
  - `AnalyticsAgent` – Gathers and analyzes data
  - `SafetyAgent` – Determines risk and flags hazards
  - `Coordinator` – Manages agent communication and execution
- **Google Vertex AI Integration** for scalable deployment of AI agents
- **Firebase Integration** for backend service management and hosting
- **Google Cloud Storage** for secure image and data storage
- **Real-time Image Processing** and **Constant Extraction Tools**
- **Modern React Frontend** with chat-style interface

---

## ⚙️ Tech Stack

### **Backend (Python)**
- Language: **Python 3.x**
- Framework: **Functions Framework** for Google Cloud Functions
- Libraries:
  - `vertexai` – Integration with Google Vertex AI
  - `google-cloud-logging` – Logging and monitoring
  - `Pillow` – Image processing

### **Frontend (hawkai-chat)**
- **React 19**
- Libraries:
  - `react-dom`, `react-markdown`
  - `react-scripts`
  - Testing: `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/dom`, `@testing-library/user-event`
  - `web-vitals`

### **Image Upload Server**
- **Node.js + Express**
- Libraries:
  - `multer` – File uploads
  - `@google-cloud/storage` – Google Cloud Storage SDK
  - `dotenv`, `cors`
- Dev tools: `nodemon`
- **Firebase Studio Hosting** for deployment

### **Cloud & Deployment**
- **Google Vertex AI** – Model hosting and orchestration
- **Google Cloud Storage (GCS)** – File and data storage
- **Firebase** – Serverless backend & hosting

---

## 🚀 Getting Started

### 1. **Backend (Python)**

```bash
cd HawkAI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

> Optional:  
> - Use `fast-main.py` or `simplified-main.py` for faster startup.  
> - Use `deploy.sh` or `vertex_ai_deployment.sh` for Google Vertex AI deployment.

---

### 2. **Frontend (React)**
```bash
cd hawkai-chat
npm install
npm start
```
> Access at: [http://localhost:3000](http://localhost:3000)

---

### 3. **Image Upload Server**
```bash
cd image-upload-server
npm install
npm run dev    # runs with nodemon
```
This service handles secure file uploads to **Google Cloud Storage**, using **Firebase** for hosting.

---

## 🧪 Testing & Tools
- Python testing: `test_function.py`, `test_image_processing.py`
- Constant extractor: `scripts/extract_constants.py`
- Configuration: `config/constants.py`

---

## ☁️ Deployment

- **Google Cloud Vertex AI**
```bash
bash vertex_ai_deployment.sh
```

- **Firebase Hosting**
```bash
firebase deploy
```

Ensure you have:
- `hawkai-key.json` for authentication  
- `agent_config.json` for agent-level deployment configuration

---

## 🔐 `.env` Configuration

Create a `.env` file in the **project root** and `image-upload-server/`:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=hawkai-467107
GOOGLE_CLOUD_BUCKET_NAME=hawkai-feedbucket
SERVICE_ACCOUNT_KEY_PATH=./config/key.json

# Upload Configuration
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,image/gif,image/webp

# Firebase Configuration
FIREBASE_PROJECT_ID=hawkai-467107
FIREBASE_API_KEY=your_firebase_api_key
```

Ensure `.env` is in `.gitignore` and never committed to source control.

---

## 🤝 Contributing
Pull requests and issues are welcome. Please ensure your code is clean, modular, and documented.

---

## 📄 License
MIT License — see `LICENSE` for details.
