import time
import random
import json
import paho.mqtt.client as mqtt
import sys
sys.stdout.reconfigure(encoding="utf-8")

BROKER = "localhost"
PORT = 1883
TEMP_TOPIC     = "mattress/temperature"
HUMIDITY_TOPIC = "mattress/humidity"
SETPOINT_TOPIC = "mattress/setpoint"
PUBLISH_INTERVAL = 3  # seconds between readings

# Tracks the current user setpoint, updated via MQTT
state = {
    "setpoint": 36.0,
}


def simulate_temperature(current_temp):
    # Slowly drift toward the setpoint with small random noise
    drift = (state["setpoint"] - current_temp) * 0.02
    noise = random.uniform(-0.1, 0.1)
    return round(current_temp + drift + noise, 2)


def simulate_humidity(current_humidity, current_temp):
    # Humidity rises when temp exceeds setpoint (body heat), drops when cooling
    drift = (current_temp - state["setpoint"]) * 0.1
    noise = random.uniform(-0.2, 0.2)
    return round(max(30.0, min(80.0, current_humidity + drift + noise)), 2)


def on_connect(client, userdata, connect_flags, reason_code, properties):
    if not reason_code.is_failure:
        print("[DHT] Connected to MQTT broker")
        client.subscribe(SETPOINT_TOPIC)
    else:
        print(f"[DHT] Connection failed: {reason_code}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        return
    if msg.topic == SETPOINT_TOPIC and payload.get("setpoint") is not None:
        state["setpoint"] = payload["setpoint"]


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dht_emulator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    temp     = 22.0  # start at room temperature
    humidity = 45.0

    print("[DHT] Starting DHT sensor emulator...")
    try:
        while True:
            temp     = simulate_temperature(temp)
            humidity = simulate_humidity(humidity, temp)
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
