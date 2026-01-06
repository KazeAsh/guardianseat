import random
import time
import pandas as pd
from datetime import datetime, timedelta

# Simulate sensor data for child safety monitoring
class SensorSimulator:

    # Simulate One hour of sensor data
    def simulate_one_hour(self):

        data_points = []

        #start with normal temperature of a car in use
        base_temp = random.uniform(18, 24)  # Comfortable temperature in in Celsius

        for minute in range(60):

            # Start time
            timestamp = datetime.now() + timedelta(minutes=minute)

            # Senario: car parked for 10 minutes, child left inside for 20 minutes, then car starts moving again
            if minute < 10:  # Driving with both adult and child
                door_state = "closed"
                engine_state = "on"
                weight_sensor_left = 15.0  # Weight of child in kg
                weight_sensor_right = 75.0  # Weight of adult in kg
            elif 10 <= minute < 30:  # Parked with child inside, adult exited
                door_state = "closed"
                engine_state = "off"
                weight_sensor_left = 15.0
                weight_sensor_right = 0.0
            else:  # Car starts moving again, adult returns
                door_state = "closed"
                engine_state = "on"
                weight_sensor_left = 15.0
                weight_sensor_right = 75.0
            
            # Simulate temperature changes
            if engine_state == "off" and minute >= 10:
                # Car is parked and heats up about 10°C in first 20 minutes
                temp_increase = min((minute - 10) * 0.5, 10)
                current_temp = base_temp + temp_increase + random.uniform(-0.5, 0.5)
            else:
                # Car is running, maintain base temp
                current_temp = base_temp + random.uniform(-1, 1)

        # Motion detection (child might move occasionally)
            motion_detected = random.random() > 0.8 if minute > 10 else True
            
            # Car data points of inside temperature, door state, engine state, weight sensors, motion detection
            data_point = {
                'timestamp': timestamp,
                'engine_state': engine_state,
                'door_state': door_state,
                'temperature_c': round(current_temp, 2),
                'weight_left_kg': weight_sensor_left,
                'weight_right_kg': weight_sensor_right,
                'motion_detected': motion_detected,
                'co2_level': random.uniform(400, 1000),  # ppm
                'humidity': random.uniform(30, 70)  # percent
            }
            
            data_points.append(data_point)
            
            # Add some noise/variation
            time.sleep(0.01)  # Small delay to simulate real sampling
        
        df = pd.DataFrame(data_points)
        df.to_csv("data/raw/sensor_data_hour.csv", index=False)
        print(f"Generated {len(df)} sensor readings")


if __name__ == "__main__":
    simulator = SensorSimulator()
    simulator.simulate_one_hour()