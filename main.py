import joblib
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import httpx  # Async HTTP client
import smtplib


from email.message import EmailMessage

def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = 'remotehms112233@gmail.com'
    msg['To'] = to_email

    # Connect to Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('remotehms112233@gmail.com', 'zwgr gfbb xqij bfmo')
        smtp.send_message(msg)





# Load the trained model
model = joblib.load("medical_rf_model.pkl")

# Define input schema using Pydantic
class PatientData(BaseModel):
    age: int
    sex: int
    bp: float
    chol: float
    fbs: float
    restecg: int
    email: str
    exng: int
    temperature: float
    o2: float
    hr: float

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():

    return {"message": "Welcome to ML-based Health Monitoring API"}
predictions = []
@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                patient_data = json.loads(data)
                patient = PatientData(**patient_data)

                # 🔥 Extract email separately
                email = patient.email

                # 🔥 Remove email from dict before passing to model
                if patient.hr > 200 or patient.hr < 50 and patient.o2 < 85:
                    avg_prediction = 1;
                else:
                    model_input_dict = patient.dict()
                    model_input_dict.pop("email")

                    input_df = pd.DataFrame([model_input_dict])

                    prediction = model.predict(input_df)[0]
                    
                    if (len(predictions) >= 10):
                        predictions.remove(predictions[0])
                    predictions.append(prediction)

                    avg_prediction = int(calculate_average(predictions))
                    
                await websocket.send_json({
                    "prediction": avg_prediction,
                    "status": "high risk" if avg_prediction == 1 else "normal"
                })

                if avg_prediction == 1:
                    try:
                        send_email(
                            "Health Monitoring Alert",
                            "Warning! HMS has detected a high risk of heart attack.",
                            email  # ✅ Send to actual patient email
                        )
                    except Exception as e:
                        print(f"Email sending failed: {e}")
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        try:
            await websocket.close()
        except:
            pass



def calculate_average(numbers):
    if not numbers:
        return 0  # Avoid division by zero
    return sum(numbers) / len(numbers)

# 👇 Background keep-alive pinger
async def keep_alive():
    await asyncio.sleep(5)  # Wait until server is fully up
    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Replace with your actual Render URL (no trailing slash)
                response = await client.get("https://health-monitoring-model.onrender.com/")
                print(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        await asyncio.sleep(260)  # Ping every 20 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())
