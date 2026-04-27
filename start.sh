#!/bin/bash
# ═══════════════════════════════════════════════════
# CrisisBridge AI — Cloud Startup Script
# ═══════════════════════════════════════════════════
# This script starts all 4 components of the system in the background.
# Run this inside your Google Cloud VM: bash start.sh
# To stop everything, run: pkill -f uvicorn && pkill -f sensor_simulator

echo "🚀 Starting CrisisBridge AI Cloud Environment..."

# 1. Main Application (Port 8000)
echo "Starting Main App (Port 8000)..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. Sensor Module API (Port 8001)
echo "Starting Sensor Module (Port 8001)..."
python -m uvicorn sensor_module.main:app --host 0.0.0.0 --port 8001 &

# 3. Live Chat Module API (Port 8002)
echo "Starting Live Chat Module (Port 8002)..."
python -m uvicorn chat_module.main:app --host 0.0.0.0 --port 8002 &

# Wait a few seconds for APIs to initialize
sleep 5

# 4. Sensor Simulator
echo "Starting Sensor Simulator..."
python -m sensor_module.simulator.sensor_simulator &

echo "✅ All systems are Go!"
echo "Main App: http://<YOUR_VM_IP>:8000"
echo "(Press Ctrl+C to exit this log view. The servers will keep running in the background.)"

# Keep script running to view output
wait
