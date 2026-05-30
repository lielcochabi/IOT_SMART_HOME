"""
Knob Emulator
Lets the user type a desired setpoint temperature via CLI,
then publishes it to mattress/setpoint.
"""
import json
import paho.mqtt.client as mqtt
import sys
sys.stdout.reconfigure(encoding="utf-8")

BROKER = "localhost"
PORT = 1883
SETPOINT_TOPIC = "mattress/setpoint"

DEFAULT_SETPOINT = 36.0
MIN_TEMP = 15.0
MAX_TEMP = 45.0


def on_connect(client, userdata, connect_flags, reason_code, properties):
    if not reason_code.is_failure:
        print("[KNOB] Connected to MQTT broker")
    else:
        print(f"[KNOB] Connection failed: {reason_code}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="knob_emulator")
    client.on_connect = on_connect
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    current_setpoint = DEFAULT_SETPOINT
    # Publish the default setpoint on startup
    client.publish(SETPOINT_TOPIC, json.dumps({"setpoint": current_setpoint}))
    print(f"[KNOB] Default setpoint published: {current_setpoint}°C")

    print("[KNOB] Knob emulator running. Enter a temperature setpoint (15–45°C) or 'q' to quit.")
    try:
        while True:
            user_input = input(f"[KNOB] Enter setpoint (current={current_setpoint}°C): ").strip()
            if user_input.lower() == "q":
                break
            try:
                value = float(user_input)
                if not (MIN_TEMP <= value <= MAX_TEMP):
                    print(f"[KNOB] Value out of range ({MIN_TEMP}–{MAX_TEMP}°C). Try again.")
                    continue
                current_setpoint = round(value, 1)
                client.publish(SETPOINT_TOPIC, json.dumps({"setpoint": current_setpoint}))
                print(f"[KNOB] Published setpoint -> {current_setpoint}°C")
            except ValueError:
                print("[KNOB] Invalid input. Enter a number.")
    except KeyboardInterrupt:
        print("[KNOB] Emulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
