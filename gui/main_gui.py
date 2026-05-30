"""
Main GUI — Personalized Adaptive Thermal Mattress
Displays live temperature, humidity, setpoint, relay state, alerts, and a historical chart.
"""
import tkinter as tk
from tkinter import ttk
import json
import threading
import sys
import os
from collections import deque
from datetime import datetime
import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db_setup import init_db, get_recent_temperatures, get_recent_alerts

BROKER = "localhost"
PORT   = 1883

TOPICS = [
    "mattress/temperature",
    "mattress/humidity",
    "mattress/setpoint",
    "mattress/relay",
    "mattress/alerts",
]

RELAY_COLORS = {
    "idle":    "#4CAF50",
    "heating": "#F44336",
    "cooling": "#2196F3",
}
ALERT_COLORS = {
    "warning": "#FFC107",
    "alarm":   "#F44336",
    "info":    "#4CAF50",
}

MAX_CHART_POINTS = 60


class SmartMattressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Thermal Mattress — Control Panel")
        self.root.configure(bg="#1E1E2E")
        self.root.geometry("950x700")
        self.root.resizable(True, True)

        self.temp_history    = deque(maxlen=MAX_CHART_POINTS)
        self.time_history    = deque(maxlen=MAX_CHART_POINTS)
        self.setpoint_history = deque(maxlen=MAX_CHART_POINTS)

        self.current_temp     = tk.StringVar(value="--")
        self.current_humidity = tk.StringVar(value="--")
        self.current_setpoint = tk.StringVar(value="--")
        self.relay_state      = tk.StringVar(value="idle")
        self.alert_var        = tk.StringVar(value="No alerts")

        self._build_ui()
        self._load_history()
        self._start_mqtt()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Header
        header = tk.Frame(self.root, bg="#11111B", pady=10)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="🛏  Smart Thermal Mattress",
            font=("Segoe UI", 18, "bold"), fg="#CDD6F4", bg="#11111B"
        ).pack()

        # Main content
        content = tk.Frame(self.root, bg="#1E1E2E")
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Left column: stats + alerts
        left = tk.Frame(content, bg="#1E1E2E")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        self._build_stat_card(left, "Temperature",  self.current_temp,     "°C", "#F38BA8")
        self._build_stat_card(left, "Humidity",     self.current_humidity, "%",  "#89DCEB")
        self._build_stat_card(left, "Setpoint",     self.current_setpoint, "°C", "#A6E3A1")
        self._build_relay_card(left)
        self._build_alerts_panel(left)

        # Right column: live chart
        right = tk.Frame(content, bg="#1E1E2E")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_chart(right)

    def _build_stat_card(self, parent, label, var, unit, color):
        card = tk.Frame(parent, bg="#313244", padx=14, pady=10, relief=tk.FLAT)
        card.pack(fill=tk.X, pady=4)
        tk.Label(card, text=label, font=("Segoe UI", 9), fg="#A6ADC8", bg="#313244").pack(anchor=tk.W)
        row = tk.Frame(card, bg="#313244")
        row.pack(anchor=tk.W)
        tk.Label(row, textvariable=var, font=("Segoe UI", 26, "bold"), fg=color, bg="#313244").pack(side=tk.LEFT)
        tk.Label(row, text=f" {unit}", font=("Segoe UI", 14), fg=color, bg="#313244").pack(side=tk.LEFT, pady=(8, 0))

    def _build_relay_card(self, parent):
        self.relay_frame = tk.Frame(parent, bg="#313244", padx=14, pady=10)
        self.relay_frame.pack(fill=tk.X, pady=4)
        tk.Label(self.relay_frame, text="Relay Status", font=("Segoe UI", 9),
                 fg="#A6ADC8", bg="#313244").pack(anchor=tk.W)
        self.relay_label = tk.Label(
            self.relay_frame, text="IDLE",
            font=("Segoe UI", 16, "bold"), fg=RELAY_COLORS["idle"], bg="#313244"
        )
        self.relay_label.pack(anchor=tk.W)

    def _build_alerts_panel(self, parent):
        frame = tk.Frame(parent, bg="#313244", padx=14, pady=10)
        frame.pack(fill=tk.X, pady=4)
        tk.Label(frame, text="Latest Alert", font=("Segoe UI", 9),
                 fg="#A6ADC8", bg="#313244").pack(anchor=tk.W)
        self.alert_label = tk.Label(
            frame, textvariable=self.alert_var,
            font=("Segoe UI", 9), fg="#A6E3A1", bg="#313244",
            wraplength=200, justify=tk.LEFT
        )
        self.alert_label.pack(anchor=tk.W)

        tk.Label(frame, text="Alert History", font=("Segoe UI", 9),
                 fg="#A6ADC8", bg="#313244").pack(anchor=tk.W, pady=(8, 2))
        self.alert_listbox = tk.Listbox(
            frame, bg="#1E1E2E", fg="#CDD6F4", font=("Consolas", 8),
            height=6, bd=0, highlightthickness=0, selectbackground="#45475A"
        )
        self.alert_listbox.pack(fill=tk.X)

    def _build_chart(self, parent):
        tk.Label(parent, text="Live Temperature vs Setpoint",
                 font=("Segoe UI", 10, "bold"), fg="#CDD6F4", bg="#1E1E2E").pack(pady=(0, 4))

        self.fig = Figure(figsize=(5.5, 4), dpi=96, facecolor="#1E1E2E")
        self.ax  = self.fig.add_subplot(111)
        self.ax.set_facecolor("#313244")
        self.ax.tick_params(colors="#A6ADC8")
        for spine in self.ax.spines.values():
            spine.set_edgecolor("#45475A")
        self.line_temp, = self.ax.plot([], [], color="#F38BA8", linewidth=2, label="Temperature")
        self.line_set,  = self.ax.plot([], [], color="#A6E3A1", linewidth=1.5,
                                        linestyle="--", label="Setpoint")
        self.ax.legend(facecolor="#313244", labelcolor="#CDD6F4", fontsize=8)
        self.ax.set_ylabel("°C", color="#A6ADC8")

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ── History Loading ───────────────────────────────────────────────────────

    def _load_history(self):
        rows = get_recent_temperatures(limit=MAX_CHART_POINTS)
        for ts, temp, _ in reversed(rows):
            self.temp_history.append(temp)
            self.time_history.append(ts)
        self._update_chart()

        alert_rows = get_recent_alerts(limit=20)
        for ts, level, msg in reversed(alert_rows):
            self.alert_listbox.insert(tk.END, f"[{level.upper()}] {ts[-8:]} {msg}")

    # ── MQTT ─────────────────────────────────────────────────────────────────

    def _start_mqtt(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="gui_client")
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        try:
            self.mqtt_client.connect(BROKER, PORT, keepalive=60)
            t = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            t.start()
        except Exception as e:
            print(f"[GUI] MQTT connection failed: {e}")

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties):
        if not reason_code.is_failure:
            for topic in TOPICS:
                client.subscribe(topic)
            print("[GUI] Connected and subscribed to all topics")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            return
        topic = msg.topic
        self.root.after(0, self._handle_message, topic, payload)

    def _handle_message(self, topic, payload):
        if topic == "mattress/temperature":
            temp = payload.get("temperature")
            if temp is not None:
                self.current_temp.set(f"{temp:.1f}")
                self.temp_history.append(temp)
                self.time_history.append(datetime.now().strftime("%H:%M:%S"))
                self._update_chart()

        elif topic == "mattress/humidity":
            hum = payload.get("humidity")
            if hum is not None:
                self.current_humidity.set(f"{hum:.1f}")

        elif topic == "mattress/setpoint":
            sp = payload.get("setpoint")
            if sp is not None:
                self.current_setpoint.set(f"{sp:.1f}")
                self.setpoint_history.append(sp)
                self._update_chart()

        elif topic == "mattress/relay":
            state = payload.get("state", "idle").lower()
            color = RELAY_COLORS.get(state, "#CDD6F4")
            self.relay_label.config(text=state.upper(), fg=color)

        elif topic == "mattress/alerts":
            level = payload.get("level", "info")
            msg   = payload.get("message", "")
            color = ALERT_COLORS.get(level, "#CDD6F4")
            self.alert_var.set(msg)
            self.alert_label.config(fg=color)
            ts = datetime.now().strftime("%H:%M:%S")
            self.alert_listbox.insert(tk.END, f"[{level.upper()}] {ts} {msg}")
            self.alert_listbox.see(tk.END)

    # ── Chart Update ──────────────────────────────────────────────────────────

    def _update_chart(self):
        temps = list(self.temp_history)
        sets  = list(self.setpoint_history)
        x     = list(range(len(temps)))

        self.line_temp.set_data(x, temps)

        if sets:
            # Pad or trim setpoint line to match temp length
            pad = len(temps) - len(sets)
            if pad > 0:
                sets = [sets[0]] * pad + sets
            self.line_set.set_data(list(range(len(sets))), sets[-len(temps):])

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()


def main():
    init_db()
    root = tk.Tk()
    app = SmartMattressGUI(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
