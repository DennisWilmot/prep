# models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# Patient visit records
class PatientVisit(Base):
    __tablename__ = "patient_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    department = Column(String(50))
    patient_count = Column(Integer)
    severity = Column(Integer)  # 1-5 scale

# Staffing prediction records
class StaffingPrediction(Base):
    __tablename__ = "staffing_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    department = Column(String(50))
    patient_count = Column(Integer)
    day_of_week = Column(Integer)
    hour_of_day = Column(Integer)
    has_event = Column(Integer)  # 0=no, 1=yes
    staff_needed = Column(Integer)
    confidence = Column(Float)