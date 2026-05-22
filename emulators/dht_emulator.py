"""
DHT Sensor Emulator
Publishes simulated temperature and humidity readings every 3 seconds.
"""
import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TEMP_TOPIC = "mattress/temperature"
HUMIDITY_TOPIC = "mattress/humidity"
PUBLISH_INTERVAL = 3  # seconds


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[DHT] Connected to MQTT broker")
    else:
        print(f"[DHT] Connection failed with code {rc}")


def main():
    client = mqtt.Client(client_id="dht_emulator")
    client.on_connect = on_connect
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    print("[DHT] Starting DHT sensor emulator...")
    try:
        while True:
            temp = round(random.uniform(20.0, 38.0), 2)
            humidity = round(random.uniform(40.0, 60.0), 2)

            client.publish(TEMP_TOPIC, json.dumps({"temperature": temp}))
            client.publish(HUMIDITY_TOPIC, json.dumps({"humidity": humidity}))
            print(f"[DHT] Published -> temp={temp}C  humidity={humidity}%")

            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("[DHT] Emulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
