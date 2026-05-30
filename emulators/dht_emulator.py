"""
DHT Sensor Emulator
Publishes simulated temperature and humidity readings every 3 seconds.
Temperature slowly rises toward body heat (~36°C) with small random variation.
"""
import time
import random
import json
import paho.mqtt.client as mqtt
import sys
sys.stdout.reconfigure(encoding="utf-8")

BROKER = "localhost"
PORT = 1883
TEMP_TOPIC = "mattress/temperature"
HUMIDITY_TOPIC = "mattress/humidity"
PUBLISH_INTERVAL = 3  # seconds

# Simulated starting conditions
base_temp = 22.0  # room temperature
base_humidity = 45.0


def simulate_temperature(current_temp, setpoint=36.0):
    """Slowly drift toward body heat with small noise."""
    drift = (setpoint - current_temp) * 0.05
    noise = random.uniform(-0.3, 0.3)
    return round(current_temp + drift + noise, 2)


def simulate_humidity(current_humidity):
    noise = random.uniform(-0.5, 0.5)
    return round(max(30.0, min(80.0, current_humidity + noise)), 2)


def on_connect(client, userdata, connect_flags, reason_code, properties):
    if not reason_code.is_failure:
        print("[DHT] Connected to MQTT broker")
    else:
        print(f"[DHT] Connection failed: {reason_code}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dht_emulator")
    client.on_connect = on_connect
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    temp = base_temp
    humidity = base_humidity

    print("[DHT] Starting DHT sensor emulator...")
    try:
        while True:
            temp = simulate_temperature(temp)
            humidity = simulate_humidity(humidity)

            client.publish(TEMP_TOPIC, json.dumps({"temperature": temp}))
            client.publish(HUMIDITY_TOPIC, json.dumps({"humidity": humidity}))
            print(f"[DHT] Published -> temp={temp}°C  humidity={humidity}%")

            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("[DHT] Emulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
