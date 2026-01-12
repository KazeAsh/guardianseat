# processing/compatible_processor.py
import numpy as np
import scipy.signal as signal
from typing import Dict, Any

class CompatibleMMWaveProcessor:
    """Signal processor that works with SciPy 1.10.1"""
    
    def __init__(self, sampling_rate=100):
        self.fs = sampling_rate
        self._init_filters_compatible()
    
    def _init_filters_compatible(self):
        """Initialize filters compatible with SciPy 1.10.1"""
        # Breathing filter
        self.breathing_b, self.breathing_a = signal.butter(
            4, [0.1, 0.5], btype='band', fs=self.fs
        )
        
        # Heartbeat filter  
        self.heartbeat_b, self.heartbeat_a = signal.butter(
            4, [0.8, 3.0], btype='band', fs=self.fs
        )
        
        # Notch filter (50 Hz interference)
        try:
            self.notch_b, self.notch_a = signal.iirnotch(50, 30, self.fs)
        except:
            # Fallback
            self.notch_b, self.notch_a = signal.butter(
                4, [49, 51], btype='bandstop', fs=self.fs
            )
    
    def process_iq_data(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Process I/Q data using compatible filters"""
        # Preprocess
        iq_array = np.array(iq_data, dtype=complex)
        iq_centered = iq_array - np.mean(iq_array)
        
        # Apply notch filter
        iq_filtered = signal.filtfilt(self.notch_b, self.notch_a, iq_centered)
        
        # Get amplitude
        amplitude = np.abs(iq_filtered)
        
        # Apply vital sign filters
        breathing_signal = signal.filtfilt(self.breathing_b, self.breathing_a, amplitude)
        heartbeat_signal = signal.filtfilt(self.heartbeat_b, self.heartbeat_a, amplitude)
        
        # Simple vital sign extraction
        breathing_peaks, _ = signal.find_peaks(breathing_signal, distance=self.fs*0.8)
        heartbeat_peaks, _ = signal.find_peaks(heartbeat_signal, distance=self.fs*0.3)
        
        breathing_bpm = len(breathing_peaks) / (len(iq_data)/self.fs/60) if len(breathing_peaks) > 1 else 0
        heartbeat_bpm = len(heartbeat_peaks) / (len(iq_data)/self.fs/60) if len(heartbeat_peaks) > 1 else 0
        
        return {
            'vital_signs': {
                'breathing_rate_bpm': round(breathing_bpm, 1),
                'heart_rate_bpm': round(heartbeat_bpm, 1),
                'breathing_confidence': min(len(breathing_peaks) * 0.2, 1.0),
                'heartbeat_confidence': min(len(heartbeat_peaks) * 0.1, 1.0),
                'vital_signs_detected': breathing_bpm > 5 or heartbeat_bpm > 40
            },
            'status': 'success',
            'samples_processed': len(iq_data)
        }

# Test it
if __name__ == "__main__":
    from utils.mmwave_simulator import MMWaveSimulator
    
    print("Testing compatible processor...")
    simulator = MMWaveSimulator(sampling_rate=100, duration=5)
    iq_data = simulator.generate_mmwave_iq_data(has_child=True)
    
    processor = CompatibleMMWaveProcessor(sampling_rate=100)
    result = processor.process_iq_data(iq_data)
    
    print(f"Result: {result}")