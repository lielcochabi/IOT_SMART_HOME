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
