# CrisisBridge AI

**Event:** Google Solution Challenge 2026 - Build with AI

**Theme:** [Rapid Crisis Response] Accelerated Emergency Response and Crisis Coordination in Hospitality.


## Overview
CrisisBridge AI is a comprehensive platform designed to accelerate emergency response and improve crisis coordination, specifically tailored for the hospitality sector. It integrates real-time sensor data, AI-powered assistance, and intelligent systems to provide immediate, actionable insights during critical situations, ensuring the safety of guests and staff.

## Google Technologies Used
This project proudly leverages the power of Google's advanced AI ecosystem to deliver real-time, life-saving capabilities:

* **Google Gemini API (`gemini-2.5-flash-lite`):** The core intelligence of the platform. Gemini processes crisis reports, synthesizes emergency protocols, and powers the live chat assistant to provide immediate, context-aware operational guidance.
* **Google Gemini Embeddings (`gemini-embedding-2`):** Drives our Retrieval-Augmented Generation (RAG) pipeline. It vectorizes hotel safety protocols and historical incident reports, allowing the system to retrieve highly relevant and accurate procedures instantly.
* **Google GenAI SDK (`google-genai`):** Seamlessly integrates the latest Google Gemini models directly into our Python backend architecture.
* **Google Fonts:** Utilizes Google Fonts for a clean, highly readable, and accessible user interface during high-stress scenarios.

## Key Features
- **AI Crisis Assistant:** A real-time conversational interface powered by Google Gemini to guide staff through emergencies step-by-step.
- **RAG Pipeline:** Instantly retrieves hotel-specific emergency procedures using FAISS and Gemini Embeddings.
- **Sensor Integration:** Monitors simulated environments (e.g., temperature, smoke, structural integrity) to detect anomalies and trigger automated alerts.
- **Live Mapping & Broadcast:** Visualizes sensor data and broadcasts critical alerts across a centralized dashboard.
- **Incident Reporting:** A unified system to log, track, and manage emergencies efficiently.

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, Google GenAI SDK, LangChain, FAISS
- **Frontend:** React, Vite
- **Database:** PostgreSQL / SQLite
- **Caching:** Redis

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/rajath-sh/CrisisBridge-AI.git
cd CrisisBridge-AI
```

### 2. Environment Configuration
Copy the example environment file and configure it with your credentials:
```bash
cp .env.example .env
```
> **Kindly note:** Ensure you add your Google Gemini API key to the `LLM_API_KEY` variable in the `.env` file to enable the AI features.

### 3. Install Dependencies
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Run the Application
Start the backend and frontend services using the provided startup script:
```bash
# Ensure the script has execution permissions
chmod +x start.sh

# Run the application
./start.sh
```
The application will launch, providing access to the backend API and the frontend dashboard.

---
*Built with ❤️ for the Google Solution Challenge 2026 by Team CrisisBridge*