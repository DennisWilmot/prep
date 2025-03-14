# main.py
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

from database import get_db, engine, Base
from models import PatientVisit, StaffingPrediction
import schemas
from ml_service import predict_staffing, load_model

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Hospital Staffing Predictor")

# Configure CORS to allow requests from our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Make sure model is loaded on startup
@app.on_event("startup")
def startup_event():
    load_model()

# API Routes
@app.get("/")
def read_root():
    return {"message": "Hospital Staffing Predictor API"}

@app.post("/predict/", response_model=schemas.PredictionOutput)
def predict(input_data: schemas.PredictionInput, db: Session = Depends(get_db)):
    # Make prediction
    result = predict_staffing(
        input_data.patient_count,
        input_data.day_of_week,
        input_data.hour_of_day,
        input_data.has_event
    )
    
    # Save prediction to database
    db_prediction = StaffingPrediction(
        department=input_data.department,
        patient_count=input_data.patient_count,
        day_of_week=input_data.day_of_week,
        hour_of_day=input_data.hour_of_day,
        has_event=input_data.has_event,
        staff_needed=result['staff_needed'],
        confidence=result['confidence']
    )
    db.add(db_prediction)
    db.commit()
    
    return result

@app.post("/patients/", response_model=dict)
def add_patient(patient: schemas.PatientVisitCreate, db: Session = Depends(get_db)):
    # Create new patient visit record
    db_patient = PatientVisit(
        department=patient.department,
        severity=patient.severity
    )
    db.add(db_patient)
    db.commit()
    
    return {"success": True, "id": db_patient.id}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for data from client
            data = await websocket.receive_text()
            input_data = json.loads(data)
            
            # Make prediction
            result = predict_staffing(
                input_data.get('patient_count', 20),
                input_data.get('day_of_week', 1),
                input_data.get('hour_of_day', 12),
                input_data.get('has_event', 0)
            )
            
            # Send prediction back to client
            await websocket.send_json(result)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)