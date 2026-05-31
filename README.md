# Personalized Adaptive Thermal Mattress — IoT Smart Home

## Project Overview
A simulated IoT system that monitors and controls a smart thermal mattress using MQTT for communication, a Data Manager for processing, SQLite for storage, and a GUI for visualization.

## System Architecture
```
DHT Sensor Emulator  ──┐
Knob Emulator        ──┤──► MQTT Broker ──► Data Manager ──► SQLite DB
Relay Emulator       ◄─┘                        │
                                                 ▼
                                            Main GUI
```

## MQTT Topic Structure
| Topic                    | Publisher         | Subscriber         |
|--------------------------|-------------------|--------------------|
| `mattress/temperature`   | DHT Emulator      | Data Manager, GUI  |
| `mattress/humidity`      | DHT Emulator      | Data Manager, GUI  |
| `mattress/setpoint`      | Knob Emulator     | Data Manager, GUI  |
| `mattress/relay`         | Data Manager      | Relay Emulator, GUI|
| `mattress/alerts`        | Data Manager      | GUI                |

## Components
- **emulators/** — DHT sensor, Knob, and Relay emulators
- **data_manager/** — Subscribes to topics, processes data, triggers alerts, controls relay
- **gui/** — Main GUI with live charts, alerts, and historical view
- **database/** — SQLite schema and helper functions

## Setup

### Requirements
```
pip install -r requirements.txt
```

### Run (in separate terminals)
1. Start Mosquitto broker: `mosquitto`
2. Start Relay emulator: `python emulators/relay_emulator.py`
3. Start DHT emulator: `python emulators/dht_emulator.py`
4. Start Knob emulator: `python emulators/knob_emulator.py`
5. Start Data Manager: `python data_manager/data_manager.py`
6. Start GUI: `python gui/main_gui.py`

## Database Schema
- `temperature_log` — timestamp, temperature, humidity
- `setpoint_history` — timestamp, setpoint
- `alerts` — timestamp, level (warning/alarm), message
