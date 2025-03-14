# ml_service.py
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from typing import Dict, Any

# Path to save our trained model
MODEL_PATH = "staffing_model.pkl"

def train_simple_model():
    """
    Trains a simple model based on some rules and synthetic data.
    In a real project, you would train this on historical hospital data.
    """
    # Create synthetic training data
    data = []
    
    for i in range(1000):
        # Random features
        patients = np.random.randint(5, 100)
        day = np.random.randint(0, 7)  # 0=Sunday, 6=Saturday
        hour = np.random.randint(0, 24)
        event = np.random.randint(0, 2)  # 0=no, 1=yes
        
        # Simple formula to determine staff needed
        staff = patients // 4  # Baseline: 1 staff per 4 patients
        
        # Adjustments
        if day >= 5:  # Weekend
            staff += 2  
        if hour < 8 or hour > 20:  # Night shift
            staff += 1
        if event == 1:  # Special event
            staff += 3
            
        # Ensure minimum staffing
        staff = max(2, staff)
        
        data.append({
            'patient_count': patients,
            'day_of_week': day,
            'hour_of_day': hour,
            'has_event': event,
            'staff_needed': staff
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # In a real model, you'd use more sophisticated ML
    # For simplicity, we'll create a lookup table
    model = {
        'data': df,
        'created_at': datetime.now()
    }
    
    # Save model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    return model

def load_model():
    """Loads the trained model or trains a new one if none exists"""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    else:
        return train_simple_model()

def predict_staffing(patient_count: int, day_of_week: int, hour_of_day: int, has_event: int) -> Dict[str, Any]:
    """
    Predict staffing needs based on input parameters
    """
    # Load model
    model = load_model()
    df = model['data']
    
    # Find similar scenarios in our data
    similar = df[
        (df['patient_count'].between(patient_count-10, patient_count+10)) & 
        (df['day_of_week'] == day_of_week) & 
        (df['hour_of_day'].between(hour_of_day-3, hour_of_day+3)) &
        (df['has_event'] == has_event)
    ]
    
    # If we find similar scenarios, take the average staff needed
    if len(similar) > 0:
        staff_needed = int(similar['staff_needed'].mean())
        confidence = min(0.9, 0.5 + (len(similar) / 100))
    else:
        # Fallback to a simple formula
        staff_needed = max(2, patient_count // 4)
        
        # Adjustments
        if day_of_week >= 5:  # Weekend
            staff_needed += 2  
        if hour_of_day < 8 or hour_of_day > 20:  # Night shift
            staff_needed += 1
        if has_event == 1:  # Special event
            staff_needed += 3
            
        confidence = 0.6
    
    return {
        'staff_needed': staff_needed,
        'confidence': confidence,
        'timestamp': datetime.now()
    }