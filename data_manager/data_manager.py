"""
Data Manager
- Subscribes to all mattress MQTT topics
- Logs data to SQLite
- Compares temperature vs setpoint and publishes relay commands
- Publishes warning/alarm alerts
"""
import json
import sys
import os
import paho.mqtt.client as mqtt
import sys
sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db_setup import init_db, insert_temperature, insert_setpoint, insert_alert

BROKER = "localhost"
PORT = 1883

TOPICS = {
    "temperature": "mattress/temperature",
    "humidity":    "mattress/humidity",
    "setpoint":    "mattress/setpoint",
}
RELAY_TOPIC  = "mattress/relay"
ALERTS_TOPIC = "mattress/alerts"

WARNING_DELTA = 2.0   # °C difference -> Warning
ALARM_DELTA   = 4.0   # °C difference -> Alarm
EXTREME_LOW   = 10.0  # °C absolute -> Alarm
EXTREME_HIGH  = 45.0  # °C absolute -> Alarm

state = {
    "temperature": None,
    "humidity":    None,
    "setpoint":    36.0,
    "relay":       "idle",
    "last_alert":  None,
}


def determine_relay_state(temp, setpoint):
    delta = temp - setpoint
    if delta < -1.0:
        return "heating"
    elif delta > 1.0:
        return "cooling"
    return "idle"


def evaluate_alerts(client, temp, setpoint):
    delta = abs(temp - setpoint)
    alert_level = None
    alert_msg = None

    if temp <= EXTREME_LOW or temp >= EXTREME_HIGH:
        alert_level = "alarm"
        alert_msg = f"EXTREME temperature detected: {temp}°C"
    elif delta >= ALARM_DELTA:
        alert_level = "alarm"
        alert_msg = f"Temperature {temp}°C is far from setpoint {setpoint}°C (delta={delta:.1f}°C)"
    elif delta >= WARNING_DELTA:
        alert_level = "warning"
        alert_msg = f"Temperature {temp}°C deviating from setpoint {setpoint}°C (delta={delta:.1f}°C)"

    if alert_level and alert_msg != state["last_alert"]:
        state["last_alert"] = alert_msg
        insert_alert(alert_level, alert_msg)
        client.publish(ALERTS_TOPIC, json.dumps({"level": alert_level, "message": alert_msg}))
        print(f"[DM] ALERT [{alert_level.upper()}] {alert_msg}")
    elif not alert_level:
        state["last_alert"] = None


def on_connect(client, userdata, connect_flags, reason_code, properties):
    if not reason_code.is_failure:
        print("[DM] Connected to MQTT broker")
        for topic in TOPICS.values():
            client.subscribe(topic)
            print(f"[DM] Subscribed to '{topic}'")
    else:
        print(f"[DM] Connection failed: {reason_code}")


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
            print(f"[DM] Temperature logged: {temp}°C")

            relay_state = determine_relay_state(temp, state["setpoint"])
            if relay_state != state["relay"]:
                state["relay"] = relay_state
                client.publish(RELAY_TOPIC, json.dumps({"state": relay_state}))
                print(f"[DM] Relay command -> {relay_state}")

            evaluate_alerts(client, temp, state["setpoint"])

    elif topic == TOPICS["humidity"]:
        humidity = payload.get("humidity")
        if humidity is not None:
            state["humidity"] = humidity

    elif topic == TOPICS["setpoint"]:
        setpoint = payload.get("setpoint")
        if setpoint is not None:
            state["setpoint"] = setpoint
            insert_setpoint(setpoint)
            print(f"[DM] Setpoint updated: {setpoint}°C")


def main():
    init_db()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="data_manager")
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
