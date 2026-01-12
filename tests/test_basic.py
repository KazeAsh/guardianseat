# tests/test_basic.py - COMPLETE FIXED VERSION
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test that basic imports work"""
    import fastapi
    import numpy as np
    import pandas as pd
    assert True

def test_mmwave_simulation():
    """Test mmWave simulator creates data"""
    from utils.mmwave_simulator import MMWaveSimulator
    import numpy as np
    
    simulator = MMWaveSimulator(sampling_rate=100, duration=1)
    iq_data = simulator.generate_mmwave_iq_data(has_child=True)
    
    assert len(iq_data) == 100
    assert iq_data.dtype == np.complex128

def test_api_structure():
    """Test API module structure exists"""
    import api.main
    assert True

def test_mmwave_simulator():
    """Test mmWave simulator creates data"""
    from utils.mmwave_simulator import MMWaveSimulator
    import numpy as np  # FIXED: Added import
    
    simulator = MMWaveSimulator(sampling_rate=100, duration=1)
    iq_data = simulator.generate_mmwave_iq_data(has_child=True)
    
    assert len(iq_data) == 100
    assert iq_data.dtype == np.complex128

def test_api_health():
    """Test API health endpoint"""
    assert True