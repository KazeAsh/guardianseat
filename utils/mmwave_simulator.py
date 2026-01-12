import numpy as np
import pandas as pd
import scipy.signal as signal
from datetime import datetime, timedelta
import json
import os

# Simulate mmWave radar based vital signal detection
# Based on real mmWave radar principles (FMCW radar)
class MMWaveSimulator:

    def __init__(self, sampling_rate=100, duration=60):
        
        self.fs = sampling_rate  # Sampling rate in Hz
        self.duration = duration  # Duration in seconds
        self.times = np.arange(0, duration, 1/sampling_rate)
        
        # Vital sign parameters
        self.adult_heart_rate = 60-100 # bpm
        self.child_heart_rate = 100-160 # bpm
        self.adult_breathing_rate = 12-20 # bpm
        self.child_breathing_rate = 20-30 # bpm

        # Car seat vibration parameters
        self.car_seat_vibration_frequency = 10  # Hz (typical for car seats)
        self.car_seat_vibration_amplitude = 0.1  # m/s^2

        # Car environment noise parameters
        self.car_noise_level = 0.05  # m/s^2

        # Car environment parameters temperature and seat pressure
        self.car_temp_range = (0, 75)  # Celsius
        self.seat_pressure_adult = (0, 200) # kg

       # Generate simulated I/Q data from mmWave radar
       # I/Q = In-phase and Quadrature components
       # Returns simulated I/Q data for realistic vital signs and car environment
    
    def generate_mmwave_iq_data(self, has_child=True, movement_level='low'):
        # Base signal (car interior reflections)

        num_samples = len(self.times)
        base_signal = 0.5 * np.sin(2 * np.pi * self.car_seat_vibration_frequency * self.times)

        if has_child:
            # Child vital signs
            child_signal = self._generate_child_vital_signs()
            radar_signal = base_signal + child_signal * 0.3

        else:
            # Empty car - only base signal
            radar_signal = base_signal

        # Add micro-movements (breathing, heartbeat)
        radar_signal = self._add_micro_movements(radar_signal, has_child, movement_level)
        # Add random noise (realistic SNR)
        radar_signal = radar_signal.astype(np.complex128)
        noise = np.random.normal(0, 0.05, num_samples) + 1j * np.random.normal(0, 0.05, num_samples)
        radar_signal += noise
            
        return radar_signal
    

    # Generate realistic child vital sign patterns
    def _generate_child_vital_signs(self):

        num_samples = len(self.times)

        # Child breating: 0.3-0.5 Hz (18-30 breaths/min)
        breating_freq = np.random.uniform(0.3, 0.5)
        breathing_signal = 0.02 * np.sin(2 * np.pi * breating_freq * self.times + np.random.uniform(0, 2*np.pi))

        # Child heartbeat: 1.3-2.0 Hz (78-120 BPM)
        heart_freq = np.random.uniform(1.3, 2.0)
        heart_signal = 0.3 * np.sin(2 * np.pi * heart_freq * self.times)

        # Harmonic components (realistic for radar)
        harmonics = 0.1 * np.sin(2 * np.pi * 2 * heart_freq * self.times)

        return breathing_signal + heart_signal + harmonics
    
    # Add realistic micro-movements based on child activity level in car
    def _add_micro_movements(self, signal, has_child, movement_level):

        num_samples = len(self.times)
        micro_movement_signal = np.zeros(num_samples)

        if has_child:
            # Child breathing and heartbeat
            micro_movement_signal += self._generate_child_vital_signs()

            # Add movement based on activity level
            if movement_level == 'sleeping':
                # Minimal movement, only breathing
                micro_movement_signal += 0.005 * np.random.normal(0, 1, num_samples)
                
            elif movement_level == 'low':
                # Quiet activity - fidgeting, slight shifts
                micro_movement_signal += 0.015 * np.random.normal(0, 1, num_samples)
                # Occasional small position shifts every 5-10 seconds
                for i in range(0, num_samples, np.random.randint(500, 1000)):
                    micro_movement_signal[i:min(i+50, num_samples)] += 0.02 * np.sin(2 * np.pi * 0.5 * self.times[:min(50, num_samples-i)])
                    
            elif movement_level == 'medium':
                # Active - squirming, seat adjustments
                micro_movement_signal += 0.04 * np.random.normal(0, 1, num_samples)
                # Regular movement bursts every 3-5 seconds
                for i in range(0, num_samples, np.random.randint(300, 500)):
                    micro_movement_signal[i:min(i+100, num_samples)] += 0.06 * np.sin(2 * np.pi * 1.5 * self.times[:min(100, num_samples-i)])
                    
            elif movement_level == 'high':
                # Very active - kicking, twisting, restless
                micro_movement_signal += 0.08 * np.random.normal(0, 1, num_samples)
                # Frequent large movements
                for i in range(0, num_samples, np.random.randint(100, 300)):
                    micro_movement_signal[i:min(i+150, num_samples)] += 0.1 * np.sin(2 * np.pi * 2.5 * self.times[:min(150, num_samples-i)])

        return signal + micro_movement_signal
    
    def extract_vital_signs(self, iq_data):
        """
        Process I/Q data to extract vital signs using signal processing
        This mimics real mmWave radar processing pipeline
        """
        # Convert to amplitude (real signal)
        amplitude = np.abs(iq_data)
        
        # Apply bandpass filters for vital signs
        # Breathing: 0.1-0.5 Hz (6-30 breaths/min)
        breathing_filter = signal.butter(4, [0.1, 0.5], btype='band', fs=self.fs, output='sos')
        breathing_signal = signal.sosfilt(breathing_filter, amplitude)
        
        # Heartbeat: 0.8-3.0 Hz (48-180 BPM)
        heartbeat_filter = signal.butter(4, [0.8, 3.0], btype='band', fs=self.fs, output='sos')
        heartbeat_signal = signal.sosfilt(heartbeat_filter, amplitude)
        
        # Calculate vital signs from filtered signals
        vital_signs = self._analyze_vital_signs(breathing_signal, heartbeat_signal)
        
        return vital_signs
    
    def _analyze_vital_signs(self, breathing_signal, heartbeat_signal):
        """Extract BPM from filtered signals"""
        # Find peaks in breathing signal
        breathing_peaks, _ = signal.find_peaks(breathing_signal, distance=self.fs*0.8)  # Min 0.8s between breaths
        breathing_bpm = len(breathing_peaks) / (self.duration / 60) if len(breathing_peaks) > 1 else 0
        
        # Find peaks in heartbeat signal
        heartbeat_peaks, _ = signal.find_peaks(heartbeat_signal, distance=self.fs*0.3)  # Min 0.3s between beats
        heartbeat_bpm = len(heartbeat_peaks) / (self.duration / 60) if len(heartbeat_peaks) > 1 else 0
        
        # Calculate signal quality metrics
        breathing_confidence = min(len(breathing_peaks) * 0.2, 1.0)
        heartbeat_confidence = min(len(heartbeat_peaks) * 0.1, 1.0)
        
        return {
            'breathing_rate_bpm': round(breathing_bpm, 1),
            'heart_rate_bpm': round(heartbeat_bpm, 1),
            'breathing_confidence': round(breathing_confidence, 2),
            'heartbeat_confidence': round(heartbeat_confidence, 2),
            'vital_signs_detected': breathing_bpm > 5 or heartbeat_bpm > 40
        }
    
    def generate_scenario_dataset(self, num_scenarios=50):
        """Generate multiple scenarios for training/validation"""
        scenarios = []
        
        for i in range(num_scenarios):
            # Randomly determine scenario
            has_child = np.random.random() > 0.3  # 70% have children
            movement_level = np.random.choice(['low', 'medium', 'high'], p=[0.5, 0.3, 0.2])
            
            # Generate radar data
            iq_data = self.generate_mmwave_iq_data(has_child, movement_level)
            
            # Extract vital signs
            vital_signs = self.extract_vital_signs(iq_data)
            
            # Add car sensor data
            car_data = self.generate_car_sensor_data(has_child)
            
            scenario = {
                'scenario_id': f'scenario_{i:03d}',
                'timestamp': datetime.now().isoformat(),
                'has_child': has_child,
                'movement_level': movement_level,
                'vital_signs': vital_signs,
                'car_sensors': car_data,
                'radar_metadata': {
                    'sampling_rate': self.fs,
                    'duration': self.duration,
                    'samples': len(iq_data),
                    'iq_mean': np.mean(np.abs(iq_data)),
                    'iq_std': np.std(np.abs(iq_data))
                }
            }
            
            scenarios.append(scenario)
            
            # Save raw I/Q data (first 1000 samples for demonstration)
            if i < 5:  # Save only first 5 for demo
                raw_data = {
                    'iq_real': np.real(iq_data)[:1000].tolist(),
                    'iq_imag': np.imag(iq_data)[:1000].tolist(),
                    'time': self.times[:1000].tolist()
                }
                
                os.makedirs('data/raw/mmwave', exist_ok=True)
                with open(f'data/raw/mmwave/scenario_{i:03d}_iq.json', 'w') as f:
                    json.dump(raw_data, f, indent=2)
        
        return scenarios
    
    def generate_car_sensor_data(self, has_child):
        """Generate realistic car sensor data"""
        # Seat pressure sensors
        if has_child:
            seat_pressure = np.random.uniform(8, 25)  # Child weight 8-25 kg
        else:
            seat_pressure = np.random.uniform(0, 2)  # Empty or light object
        
        # Temperature simulation (car heats up when closed)
        base_temp = np.random.uniform(15, 25)
        car_closed = np.random.random() > 0.5
        if car_closed:
            # Car heats up 10-20°C over time
            temp_increase = np.random.uniform(10, 20)
            current_temp = base_temp + temp_increase
        else:
            current_temp = base_temp
        
        # Door/engine state
        door_states = ['open', 'closed']
        engine_states = ['on', 'off']
        
        return {
            'seat_pressure_kg': round(seat_pressure, 1),
            'temperature_c': round(current_temp, 1),
            'door_state': np.random.choice(door_states, p=[0.2, 0.8]),
            'engine_state': np.random.choice(engine_states, p=[0.3, 0.7]),
            'co2_ppm': np.random.uniform(400, 1500),
            'humidity_percent': np.random.uniform(30, 80)
        }
    
    def save_dataset(self, scenarios, filename='mmwave_dataset.json'):
        """Save generated dataset"""
        os.makedirs('data/processed', exist_ok=True)
        
        dataset = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'num_scenarios': len(scenarios),
                'sampling_rate': self.fs,
                'duration': self.duration,
                'description': 'Simulated mmWave radar dataset for child detection'
            },
            'scenarios': scenarios
        }
        
        with open(f'data/processed/{filename}', 'w') as f:
            json.dump(dataset, f, indent=2, default=str)
        
        print(f"Dataset saved: {len(scenarios)} scenarios")
        return dataset

# Real-world data collection using OpenWeather API
class EnvironmentalDataCollector:
    """Collect real environmental data for context"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "YOUR_OPENWEATHER_API_KEY"
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city="Tokyo"):
        """Get real weather data"""
        import requests
        
        url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    'city': city,
                    'temperature_c': data['main']['temp'],
                    'feels_like_c': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'weather': data['weather'][0]['main'],
                    'wind_speed': data['wind']['speed'],
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'openweathermap'
                }
                return weather_info
        except Exception as e:
            print(f"Error fetching weather: {e}")
        
        return None
    
    def get_forecast(self, city="Tokyo", days=1):
        """Get weather forecast"""
        import requests
        
        url = f"{self.base_url}/forecast?q={city}&appid={self.api_key}&units=metric&cnt={days*8}"  # 8 forecasts per day
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                for forecast in data['list'][:days*2]:  # First few forecasts
                    forecasts.append({
                        'time': forecast['dt_txt'],
                        'temp_c': forecast['main']['temp'],
                        'humidity': forecast['main']['humidity'],
                        'description': forecast['weather'][0]['description']
                    })
                return forecasts
        except Exception as e:
            print(f"Error fetching forecast: {e}")
        
        return None

# Main script to generate data
if __name__ == "__main__":
    print("🚗 GuardianSensor: mmWave Radar Data Generation")
    print("=" * 50)
    
    # Create directories
    os.makedirs('data/raw/mmwave', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Generate mmWave radar data
    print("\n1. Generating mmWave radar simulations...")
    simulator = MMWaveSimulator(sampling_rate=100, duration=60)
    scenarios = simulator.generate_scenario_dataset(num_scenarios=20)
    dataset = simulator.save_dataset(scenarios, 'mmwave_vital_signs.json')
    
    # Show sample data
    print(f"\n2. Generated {len(scenarios)} scenarios")
    sample = scenarios[0]
    print(f"\nSample scenario (has_child={sample['has_child']}):")
    print(f"  Vital signs: {sample['vital_signs']}")
    print(f"  Car sensors: {sample['car_sensors']}")
    
    # Collect real weather data
    print("\n3. Collecting real environmental data...")
    env_collector = EnvironmentalDataCollector()
    weather = env_collector.get_current_weather("Tokyo")
    
    if weather:
        print(f"\nCurrent weather in Tokyo:")
        print(f"  Temperature: {weather['temperature_c']}°C")
        print(f"  Humidity: {weather['humidity']}%")
        print(f"  Conditions: {weather['weather']}")
        
        # Save weather data
        with open('data/processed/weather_data.json', 'w') as f:
            json.dump(weather, f, indent=2)
    
    print("\nData generation complete!")
    print("Raw data: data/raw/mmwave/")
    print("Processed data: data/processed/")