# Backend API (FastAPI)

This FastAPI server hosts the ML model and exposes prediction endpoints and a WebSocket.

## Features

- Accepts patient data over WebSocket
- Returns health risk prediction (normal / high risk)
- Sends email alerts via Gmail SMTP

## Local Setup

1. Install Python 3.8+
2. Install dependencies:
    pip install fastapi uvicorn pandas joblib httpx python-multipart

3. Ensure `main.py` and `medical_rf_model.pkl` are in the same directory

4. Run:
    uvicorn main:app --reload

5. Visit:
    http://127.0.0.1:8000

## WebSocket Endpoint

- `/ws/predict` accepts patient data and returns prediction JSON

## Deployment (Render)

- Push to GitHub
- Create Web Service on Render.com
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
