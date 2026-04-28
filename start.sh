#!/bin/bash
# ═══════════════════════════════════════════════════
# CrisisBridge AI — Cloud Startup Script
# ═══════════════════════════════════════════════════

echo "🚀 Starting CrisisBridge AI Cloud Environment..."

# Automatically activate venv if it exists
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
fi

# 1. Main Application (Port 8000)
echo "Starting Main App (Port 8000)..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. Sensor Module API (Port 8001)
echo "Starting Sensor Module (Port 8001)..."
python3 -m uvicorn sensor_module.main:app --host 0.0.0.0 --port 8001 &

# 3. Live Chat Module API (Port 8002)
echo "Starting Live Chat Module (Port 8002)..."
python3 -m uvicorn chat_module.main:app --host 0.0.0.0 --port 8002 &

# Wait a few seconds for APIs to initialize
sleep 5

# 4. Sensor Simulator
echo "Starting Sensor Simulator..."
python3 -m sensor_module.simulator.sensor_simulator &

echo "✅ All systems are Go!"
echo "Main App: http://<YOUR_VM_IP>:8000"
echo "(Check logs.txt for background output)"

# Keep script alive
wait
