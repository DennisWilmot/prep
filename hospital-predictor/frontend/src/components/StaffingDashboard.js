import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './StaffingDashboard.css';

function StaffingDashboard() {
  // State for prediction inputs
  const [inputs, setInputs] = useState({
    patient_count: 25,
    day_of_week: 1, // Monday
    hour_of_day: 12,
    has_event: 0, // No event
    department: "Emergency"
  });
  
  // State for prediction result
  const [prediction, setPrediction] = useState({
    staff_needed: 0,
    confidence: 0,
    timestamp: new Date()
  });
  
  // State for WebSocket connection
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  
  // Connect to WebSocket on component mount
  useEffect(() => {
    const newSocket = new WebSocket('ws://localhost:8000/ws');
    
    newSocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      // Send initial data
      newSocket.send(JSON.stringify(inputs));
    };
    
    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPrediction({
        ...data,
        timestamp: new Date(data.timestamp)
      });
    };
    
    newSocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };
    
    setSocket(newSocket);
    
    // Clean up on unmount
    return () => {
      newSocket.close();
    };
  }, []);
  
  // Send updated inputs to WebSocket
  useEffect(() => {
    if (socket && connected) {
      socket.send(JSON.stringify(inputs));
    }
  }, [inputs, socket, connected]);
  
  // Handle slider changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInputs(prev => ({
      ...prev,
      [name]: parseInt(value)
    }));
  };
  
  // Generate historical data for chart (simulated)
  const generateHistoricalData = () => {
    const data = [];
    const baseStaff = prediction.staff_needed;
    
    for (let hour = 0; hour < 24; hour++) {
      // Simple pattern: more staff during peak hours (8am-6pm)
      let staffNeeded = baseStaff;
      if (hour >= 8 && hour <= 18) {
        staffNeeded += 2 + Math.floor(Math.random() * 3);
      } else if (hour < 6) {
        staffNeeded -= 1 + Math.floor(Math.random() * 2);
      }
      staffNeeded = Math.max(2, staffNeeded);
      
      data.push({
        hour: `${hour}:00`,
        staffNeeded,
        currentHour: hour === inputs.hour_of_day
      });
    }
    
    return data;
  };
  
  // Get day name from number
  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day % 7];
  };
  
  const chartData = generateHistoricalData();
  
  return (
    <div className="staffing-dashboard">
      <header className="dashboard-header">
        <h1>Hospital Staffing Predictor</h1>
        <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? '🟢 Live Updates' : '🔴 Disconnected'}
        </div>
      </header>
      
      <div className="dashboard-grid">
        <div className="controls-panel">
          <h2>Adjust Parameters</h2>
          
          <div className="control-group">
            <label>Patient Count: {inputs.patient_count}</label>
            <input 
              type="range" 
              min="5" 
              max="100" 
              name="patient_count"
              value={inputs.patient_count}
              onChange={handleInputChange}
            />
          </div>
          
          <div className="control-group">
            <label>Day of Week: {getDayName(inputs.day_of_week)}</label>
            <input 
              type="range" 
              min="0" 
              max="6" 
              name="day_of_week"
              value={inputs.day_of_week}
              onChange={handleInputChange}
            />
          </div>
          
          <div className="control-group">
            <label>Hour of Day: {inputs.hour_of_day}:00</label>
            <input 
              type="range" 
              min="0" 
              max="23" 
              name="hour_of_day"
              value={inputs.hour_of_day}
              onChange={handleInputChange}
            />
          </div>
          
          <div className="control-group">
            <label>Major Event: {inputs.has_event ? 'Yes' : 'No'}</label>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="1"
              name="has_event"
              value={inputs.has_event}
              onChange={handleInputChange}
            />
          </div>
        </div>
        
        <div className="prediction-panel">
          <h2>Staffing Prediction</h2>
          
          <div className="prediction-card">
            <div className="prediction-header">
              <div className="prediction-department">{inputs.department}</div>
              <div className="prediction-confidence">
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
            
            <div className="prediction-value">
              <span className="value-label">Recommended Staff:</span>
              <span className="value-number">{prediction.staff_needed}</span>
            </div>
            
            <div className="prediction-info">
              <div className="info-item">
                <span className="info-label">Patient-to-Staff Ratio:</span>
                <span className="info-value">
                  {(inputs.patient_count / prediction.staff_needed).toFixed(1)}:1
                </span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Updated:</span>
                <span className="info-value">
                  {prediction.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
          
          <div className="chart-container">
            <h3>Staffing Needs Throughout the Day</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="staffNeeded" 
                  stroke="#8884d8" 
                  name="Staff Needed" 
                  strokeWidth={2}
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    return payload.currentHour ? 
                      <circle cx={cx} cy={cy} r={6} fill="red" /> : 
                      <circle cx={cx} cy={cy} r={3} fill="#8884d8" />;
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StaffingDashboard;