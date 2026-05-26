"""
Data Manager
- Subscribes to all mattress MQTT topics
- Logs data to SQLite
"""
import json
import sys
import os
import paho.mqtt.client as mqtt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db_setup import init_db, insert_temperature, insert_setpoint

BROKER = "localhost"
PORT = 1883

TOPICS = {
    "temperature": "mattress/temperature",
    "humidity":    "mattress/humidity",
    "setpoint":    "mattress/setpoint",
}

state = {
    "temperature": None,
    "humidity":    None,
    "setpoint":    36.0,
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[DM] Connected to MQTT broker")
        for topic in TOPICS.values():
            client.subscribe(topic)
            print(f"[DM] Subscribed to '{topic}'")
    else:
        print(f"[DM] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        print(f"[DM] Failed to parse message on {topic}")
        return

    if topic == TOPICS["temperature"]:
        temp = payload.get("temperature")
        if temp is not None:
            state["temperature"] = temp
            humidity = state["humidity"] if state["humidity"] is not None else 0.0
            insert_temperature(temp, humidity)
            print(f"[DM] Temperature logged: {temp}C")

    elif topic == TOPICS["humidity"]:
        humidity = payload.get("humidity")
        if humidity is not None:
            state["humidity"] = humidity

    elif topic == TOPICS["setpoint"]:
        setpoint = payload.get("setpoint")
        if setpoint is not None:
            state["setpoint"] = setpoint
            insert_setpoint(setpoint)
            print(f"[DM] Setpoint updated: {setpoint}C")


def main():
    init_db()
    client = mqtt.Client(client_id="data_manager")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)

    print("[DM] Data Manager running...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("[DM] Data Manager stopped.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
