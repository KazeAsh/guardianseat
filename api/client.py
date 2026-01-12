# api/client.py
import requests
import json
from datetime import datetime

class GuardianSensorClient:
    """Client to interact with the GuardianSensor API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def send_sensor_data(self, data):
        """Send sensor data to API"""
        url = f"{self.base_url}/sensors"
        response = requests.post(url, json=data)
        return response.json()
    
    def get_risk_assessment(self):
        """Get current risk assessment"""
        url = f"{self.base_url}/risk"
        response = requests.get(url)
        return response.json()
    
    def get_dashboard_data(self):
        """Get dashboard data"""
        url = f"{self.base_url}/dashboard"
        response = requests.get(url)
        return response.json()
    
    def get_alerts(self, status=None):
        """Get alerts"""
        url = f"{self.base_url}/alerts"
        params = {"status": status} if status else {}
        response = requests.get(url, params=params)
        return response.json()

# Test the API
if __name__ == "__main__":
    client = GuardianSensorClient()
    
    # Test data
    test_data = {
        "temperature_c": 38.5,
        "weight_left_kg": 15.2,
        "weight_right_kg": 0.0,
        "motion_detected": False,
        "door_state": "closed",
        "engine_state": "off",
        "timestamp": datetime.now().isoformat()
    }
    
    print("Sending sensor data...")
    result = client.send_sensor_data(test_data)
    print("Response:", json.dumps(result, indent=2))
    
    print("\nGetting risk assessment...")
    risk = client.get_risk_assessment()
    print("Risk:", json.dumps(risk, indent=2))
    
    print("\nGetting dashboard data...")
    dashboard = client.get_dashboard_data()
    print("Dashboard metrics:", json.dumps(dashboard["metrics"], indent=2))