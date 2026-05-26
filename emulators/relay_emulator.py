"""
Relay Emulator
Subscribes to mattress/relay and prints/logs the heating or cooling state.
States: idle | heating | cooling
"""
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
RELAY_TOPIC = "mattress/relay"

STATE_COLORS = {
    "idle":    "\033[37m",   # white
    "heating": "\033[91m",   # red
    "cooling": "\033[94m",   # blue
    "reset":   "\033[0m",
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[RELAY] Connected to MQTT broker")
        client.subscribe(RELAY_TOPIC)
        print(f"[RELAY] Subscribed to '{RELAY_TOPIC}'")
    else:
        print(f"[RELAY] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", "idle").lower()
        color = STATE_COLORS.get(state, STATE_COLORS["reset"])
        reset = STATE_COLORS["reset"]
        print(f"[RELAY] {color}State changed -> {state.upper()}{reset}")
    except Exception as e:
        print(f"[RELAY] Error parsing message: {e}")


def main():
    client = mqtt.Client(client_id="relay_emulator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)

    print("[RELAY] Relay emulator running...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("[RELAY] Emulator stopped.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
