# api/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GuardianSensor API", 
              description="Child-in-Vehicle Safety System API",
              version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class SensorData(BaseModel):
    temperature_c: float
    weight_left_kg: float
    weight_right_kg: float
    motion_detected: bool
    door_state: str
    engine_state: str
    timestamp: str

class AlertRequest(BaseModel):
    alert_level: str  # "warning", "critical", "emergency"
    location: str
    vehicle_id: str
    message: str

class RiskAssessment(BaseModel):
    temperature_risk: float
    time_risk: float
    occupancy_risk: float
    total_risk: float
    recommendation: str

# Global state (in production, use a database)
alerts_db = []
sensor_data_history = []

class RiskCalculator:
    """Calculates risk score based on sensor data"""
    
    @staticmethod
    def calculate_risk(sensor_data: Dict[str, Any]) -> RiskAssessment:
        """Calculate comprehensive risk score"""
        
        # 1. Temperature risk (0-1)
        temp = sensor_data.get('temperature_c', 25)
        if temp > 40:
            temp_risk = 1.0
        elif temp > 26:
            temp_risk = (temp - 26) / 14  # Linear from 26-40°C
        else:
            temp_risk = 0.0
        
        # 2. Time risk (based on how long car has been off)
        # In real system, would track elapsed time
        time_risk = 0.0  # Placeholder
        
        # 3. Occupancy risk
        weight_left = sensor_data.get('weight_left_kg', 0)
        weight_right = sensor_data.get('weight_right_kg', 0)
        
        # Pattern: Child in left seat, no adult in right
        if weight_left > 2 and weight_left < 25 and weight_right < 5:
            occupancy_risk = 0.8
        elif weight_left > 2 and weight_left < 25:
            occupancy_risk = 0.5
        else:
            occupancy_risk = 0.0
        
        # 4. Motion risk (no motion is worse)
        motion = sensor_data.get('motion_detected', True)
        motion_risk = 0.0 if motion else 0.3
        
        # 5. Door/engine state
        door_closed = sensor_data.get('door_state') == 'closed'
        engine_off = sensor_data.get('engine_state') == 'off'
        state_risk = 0.4 if (door_closed and engine_off) else 0.0
        
        # Total risk (weighted average)
        total_risk = (
            temp_risk * 0.3 +
            occupancy_risk * 0.3 +
            state_risk * 0.2 +
            motion_risk * 0.1 +
            time_risk * 0.1
        )
        
        # Recommendation
        if total_risk > 0.7:
            recommendation = "EMERGENCY: Immediate intervention required"
        elif total_risk > 0.4:
            recommendation = "WARNING: Check vehicle immediately"
        elif total_risk > 0.2:
            recommendation = "CAUTION: Monitor situation"
        else:
            recommendation = "SAFE: No immediate risk detected"
        
        return RiskAssessment(
            temperature_risk=round(temp_risk, 2),
            time_risk=round(time_risk, 2),
            occupancy_risk=round(occupancy_risk, 2),
            total_risk=round(total_risk, 2),
            recommendation=recommendation
        )

class AlertSystem:
    """Manages alert notifications"""
    
    @staticmethod
    def send_alert(level: str, vehicle_id: str, risk_data: Dict[str, Any]):
        """Simulate sending alerts to different channels"""
        
        alert_messages = {
            "warning": {
                "title": "Vehicle Safety Warning!",
                "message": f"Unattended child detected in vehicle {vehicle_id}",
                "actions": ["Check vehicle", "Acknowledge"]
            },
            "critical": {
                "title": "Critical Alert!!",
                "message": f"Dangerous conditions in vehicle {vehicle_id}. Temperature: {risk_data.get('temperature', 0)}°C",
                "actions": ["Emergency contact", "View live feed"]
            },
            "emergency": {
                "title": "EMERGENCY",
                "message": f"Child in distress in vehicle {vehicle_id}. Contacting emergency services.",
                "actions": ["Call 911", "Share location"]
            }
        }
        
        alert = {
            "id": len(alerts_db) + 1,
            "level": level,
            "vehicle_id": vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "data": risk_data,
            "message": alert_messages.get(level, {}).get("message", ""),
            "actions": alert_messages.get(level, {}).get("actions", []),
            "status": "active"
        }
        
        alerts_db.append(alert)
        logger.info(f"Alert sent: {level} for vehicle {vehicle_id}")
        
        # In production, would send:
        # 1. Push notification to parent
        # 2. SMS
        # 3. Email
        # 4. Emergency services API call
        
        return alert

# API Endpoints

@app.get("/")
async def root():
    return {
        "service": "GuardianSensor API",
        "version": "1.0.0",
        "endpoints": [
            "/sensors - POST sensor data",
            "/risk - GET risk assessment",
            "/alerts - GET alerts",
            "/dashboard - GET dashboard data"
        ]
    }

@app.post("/sensors", response_model=Dict[str, Any])
async def receive_sensor_data(data: SensorData):
    """Receive sensor data from vehicle"""
    
    # Convert to dict
    sensor_dict = data.dict()
    sensor_dict["received_at"] = datetime.now().isoformat()
    
    # Store in history (in production, use database)
    sensor_data_history.append(sensor_dict)
    
    # Calculate risk
    risk_calc = RiskCalculator()
    risk_assessment = risk_calc.calculate_risk(sensor_dict)
    
    # Trigger alerts if needed
    if risk_assessment.total_risk > 0.7:
        alert_system = AlertSystem()
        alert_system.send_alert(
            level="emergency",
            vehicle_id="test_vehicle_001",
            risk_data=risk_assessment.dict()
        )
    elif risk_assessment.total_risk > 0.4:
        alert_system = AlertSystem()
        alert_system.send_alert(
            level="critical",
            vehicle_id="test_vehicle_001",
            risk_data=risk_assessment.dict()
        )
    elif risk_assessment.total_risk > 0.2:
        alert_system = AlertSystem()
        alert_system.send_alert(
            level="warning",
            vehicle_id="test_vehicle_001",
            risk_data=risk_assessment.dict()
        )
    
    return {
        "status": "success",
        "message": "Sensor data received",
        "risk_assessment": risk_assessment.dict(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/risk", response_model=RiskAssessment)
async def get_risk_assessment():
    """Get current risk assessment"""
    if not sensor_data_history:
        raise HTTPException(status_code=404, detail="No sensor data available")
    
    latest_data = sensor_data_history[-1]
    risk_calc = RiskCalculator()
    return risk_calc.calculate_risk(latest_data)

@app.get("/alerts")
async def get_alerts(status: Optional[str] = None, limit: int = 10):
    """Get alert history"""
    filtered_alerts = alerts_db
    
    if status:
        filtered_alerts = [a for a in alerts_db if a["status"] == status]
    
    return {
        "count": len(filtered_alerts),
        "alerts": filtered_alerts[-limit:]  # Most recent first
    }

@app.get("/dashboard")
async def get_dashboard_data():
    """Get data for dashboard visualization"""
    
    if not sensor_data_history:
        # Return sample data
        return {
            "metrics": {
                "total_alerts": 0,
                "active_alerts": 0,
                "avg_temperature": 25.0,
                "risk_trend": "stable"
            },
            "recent_alerts": [],
            "sensor_history": []
        }
    
    # Calculate metrics
    recent_alerts = alerts_db[-5:] if alerts_db else []
    recent_sensors = sensor_data_history[-20:] if sensor_data_history else []
    
    active_alerts = len([a for a in alerts_db if a.get("status") == "active"])
    
    # Temperature stats
    temperatures = [s.get("temperature_c", 0) for s in sensor_data_history[-10:]]
    avg_temp = sum(temperatures) / len(temperatures) if temperatures else 0
    
    return {
        "metrics": {
            "total_alerts": len(alerts_db),
            "active_alerts": active_alerts,
            "avg_temperature": round(avg_temp, 1),
            "risk_trend": "increasing" if len(alerts_db) > 2 else "stable"
        },
        "recent_alerts": recent_alerts,
        "sensor_history": recent_sensors
    }

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    """Mark alert as resolved"""
    if alert_id < 1 or alert_id > len(alerts_db):
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alerts_db[alert_id - 1]["status"] = "resolved"
    alerts_db[alert_id - 1]["resolved_at"] = datetime.now().isoformat()
    
    return {"status": "success", "message": f"Alert {alert_id} resolved"}

# Background task to simulate periodic sensor updates
async def simulate_sensor_updates():
    """Background task that simulates incoming sensor data"""
    import random
    import asyncio
    
    while True:
        await asyncio.sleep(10)  # Every 10 seconds
        
        if len(sensor_data_history) < 100:  # Don't overload
            simulated_data = SensorData(
                temperature_c=round(random.uniform(20, 45), 1),
                weight_left_kg=round(random.uniform(0, 20), 1),
                weight_right_kg=round(random.uniform(0, 80), 1),
                motion_detected=random.random() > 0.5,
                door_state=random.choice(["open", "closed"]),
                engine_state=random.choice(["on", "off"]),
                timestamp=datetime.now().isoformat()
            )
            
            # Process the data
            await receive_sensor_data(simulated_data)
            
            logger.info(f"Simulated sensor update: {simulated_data.temperature_c}°C")

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    asyncio.create_task(simulate_sensor_updates())

@app.get("/health")
async def health_check():
    """Health check endpoint for CI/CD and monitoring"""
    return {
        "status": "healthy",
        "service": "GuardianSensor API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Run the server
if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)