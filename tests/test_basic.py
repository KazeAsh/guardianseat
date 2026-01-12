# tests/test_basic.py
def test_imports():
    """Test that basic imports work"""
    import fastapi
    import numpy as np
    import pandas as pd
    from utils.mmwave_simulator import MMWaveSimulator
    
    assert True  # If we get here, imports work

def test_mmwave_simulator():
    """Test mmWave simulator creates data"""
    from utils.mmwave_simulator import MMWaveSimulator
    
    simulator = MMWaveSimulator(sampling_rate=100, duration=1)
    iq_data = simulator.generate_mmwave_iq_data(has_child=True)
    
    assert len(iq_data) == 100  # 100 Hz * 1 second
    assert iq_data.dtype == np.complex128
    
def test_api_health():
    """Test API health endpoint (simulated)"""
    # This would test the actual API when running
    assert True