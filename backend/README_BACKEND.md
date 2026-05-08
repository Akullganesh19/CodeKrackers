# VSDP Backend — Operational Guide

The VSDP backend is built using **FastAPI** to handle heavy lifting like AI Smishing classification, real-time telemetry, and future blockchain evidence logging.

## 🛠️ Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)

## 📦 Installation

1. Open a terminal in the `backend` directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Backend

Start the FastAPI server:
```bash
python main.py
```
The server will start at **http://localhost:8000**.

---

## 📡 API Endpoints

### 1. SMS Scanner
- **Endpoint**: `POST /api/scan-sms`
- **Payload**: `{ "text": "SMS content here" }`
- **Logic**: Uses a simulated neural network (BERT-style) to classify messages as SAFE or SCAM.

### 2. Platform Stats
- **Endpoint**: `GET /api/stats`
- **Description**: Returns live metrics for the dashboard (Blocked scams, active threats, etc.).

### 3. Threat Alerts
- **Endpoint**: `GET /api/threat-alerts`
- **Description**: Returns a list of the most recent interceptions for the Live Telemetry feed.

---

## 🛡️ Security Features
- **CORS Enabled**: Configured to allow requests from the Next.js frontend (localhost:3000).
- **Type Validation**: Uses Pydantic for strict input/output validation.
- **Async Processing**: Ready for high-concurrency real-time scanning.
