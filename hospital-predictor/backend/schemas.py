# schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Input model for prediction requests
class PredictionInput(BaseModel):
    patient_count: int
    day_of_week: int
    hour_of_day: int
    has_event: int
    department: str = "Emergency"

# Output model for prediction responses
class PredictionOutput(BaseModel):
    staff_needed: int
    confidence: float
    timestamp: datetime

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models

# Patient visit input model
class PatientVisitCreate(BaseModel):
    department: str
    severity: int