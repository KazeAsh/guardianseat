#!/usr/bin/env python3
"""
GuardianSensor - Main Entry Point
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    print("íº— GuardianSensor - mmWave Radar Child Safety System")
    print("=" * 50)
    print("\nAvailable commands:")
    print("  python run.py api        - Start the FastAPI server")
    print("  python run.py dashboard  - Start the Streamlit dashboard")
    print("  python run.py process    - Run signal processing pipeline")
    print("  python run.py simulate   - Generate simulation data")
    print("  python run.py test       - Run tests")
    print("\nOr use the individual module files directly.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "api":
            import uvicorn
            uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
        elif command == "dashboard":
            import subprocess
            subprocess.run(["streamlit", "run", "dashboard/app.py"])
        elif command == "process":
            from processing.mmwave_processor import MMWaveProcessor
            processor = MMWaveProcessor()
            # Add your processing logic here
            print("Starting signal processing...")
        elif command == "simulate":
            from utils.mmwave_simulator import MMWaveSimulator
            simulator = MMWaveSimulator()
            simulator.generate_scenario_dataset(num_scenarios=10)
            print("Simulation data generated!")
        elif command == "test":
            import pytest
            pytest.main(["-v", "tests/"])
        else:
            print(f"Unknown command: {command}")
            main()
    else:
        main()
