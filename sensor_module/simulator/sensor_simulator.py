"""
Sensor Simulator — Continuous Live Streaming
=============================================
- Always streams NORMAL (safe) readings.
- Dynamically fetches the sensor list from the API, so any sensor
  registered by the admin is automatically included in the stream.
- Spikes ONLY fire when an admin queues them via POST /sensor/queue-spike.
  The spike is consumed by the API (exactly once) and the stream
  automatically returns to normal after that single reading.

How to run:
    python -m sensor_module.simulator.sensor_simulator

How to trigger a controlled spike during the demo:
    → Swagger UI: POST /sensor/queue-spike?sensor_id=S2
    → The very next reading from S2 will be a spike.
    → After that ONE reading, everything returns to normal automatically.
"""

import time
import random
import requests
import os
from datetime import datetime

# ── Configuration ────────────────────────────────────
SENSOR_API_URL   = os.getenv("SENSOR_API_URL", "http://localhost:8001")
INTERVAL_SECONDS = 3   # One reading every 3 seconds


def fetch_sensors() -> list:
    """
    Dynamically fetches the current sensor list from the API.
    This means any sensor added/removed by the admin is automatically
    picked up by the simulator on its next fetch.
    Returns an empty list if the server is unreachable.
    """
    try:
        resp = requests.get(f"{SENSOR_API_URL}/sensor/list", timeout=3)
        return resp.json()  # List of sensor dicts
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []


def generate_normal_value(threshold: float) -> float:
    """
    Generates a safe, normal reading well below the threshold.
    Simulates realistic IoT sensor noise.
    """
    # Safe range: 20–50 units below threshold, min 0
    return round(max(0, threshold - random.uniform(20, 50)), 2)


def post_reading(sensor_id: str, value: float, threshold: float):
    """Posts a sensor reading to the API and prints the result."""
    payload = {
        "sensor_id": sensor_id,
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(
            f"{SENSOR_API_URL}/sensor/data",
            json=payload,
            timeout=5
        )
        result = response.json()
        status = result.get("status", "UNKNOWN")
        ts     = datetime.now().strftime("%H:%M:%S")

        if status == "SPIKE_DETECTED":
            # The API overrode our value because a spike was queued!
            spike_val = result.get("alert", {}).get("value", value)
            print(
                f"[{ts}] 🚨 SPIKE!  Sensor={sensor_id} | "
                f"Value={spike_val} > Threshold={threshold}"
            )
        else:
            print(
                f"[{ts}] ✅ normal  Sensor={sensor_id} | Value={value}"
            )

    except requests.exceptions.ConnectionError:
        print(
            f"❌ Cannot reach {SENSOR_API_URL}. "
            "Is 'uvicorn sensor_module.main:app --port 8001' running?"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


def run_simulator():
    """
    Main simulation loop — Round-Robin mode.
    Every registered sensor sends exactly ONE reading per cycle,
    in order. New sensors added via API are picked up on the next cycle.
    """
    print("=" * 60)
    print("  CrisisBridge — Live Sensor Simulator (Round-Robin)")
    print(f"  API:      {SENSOR_API_URL}")
    print(f"  Interval: {INTERVAL_SECONDS}s per sensor  |  Mode: ROUND-ROBIN")
    print()
    print("  ✅ Every sensor sends data every cycle — no skipping.")
    print("  ✅ Automatically includes sensors added via API.")
    print("  ✅ Automatically excludes sensors deleted via API.")
    print()
    print("  To trigger a spike:")
    print("  → Swagger UI: POST /sensor/queue-spike?sensor_id=S2")
    print("  → It fires EXACTLY ONCE, then returns to normal.")
    print("=" * 60)

    while True:
        # Fetch the live sensor list at the start of every cycle
        sensors = fetch_sensors()

        if not sensors:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                "⚠️  No sensors registered. Add one via POST /sensor/register."
            )
            time.sleep(INTERVAL_SECONDS)
            continue

        print(f"\n--- Cycle: {len(sensors)} sensors active ---")

        # Send one reading per sensor, in order
        for sensor in sensors:
            sensor_id = sensor["sensor_id"]
            threshold = sensor["threshold"]
            value     = generate_normal_value(threshold)
            post_reading(sensor_id, value, threshold)
            time.sleep(INTERVAL_SECONDS)



if __name__ == "__main__":
    try:
        run_simulator()
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")
