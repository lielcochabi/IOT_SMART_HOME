"""
Main GUI - Personalized Adaptive Thermal Mattress
Adds relay status card and alerts panel.
"""
import tkinter as tk
from tkinter import ttk

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


class SmartMattressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Thermal Mattress - Control Panel")
        self.root.configure(bg="#1E1E2E")
        self.root.geometry("950x700")
        self.root.resizable(True, True)

        self.current_temp     = tk.StringVar(value="--")
        self.current_humidity = tk.StringVar(value="--")
        self.current_setpoint = tk.StringVar(value="--")
        self.relay_state      = tk.StringVar(value="idle")
        self.alert_var        = tk.StringVar(value="No alerts")

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        header = tk.Frame(self.root, bg="#11111B", pady=10)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="Smart Thermal Mattress",
            font=("Segoe UI", 18, "bold"), fg="#CDD6F4", bg="#11111B"
        ).pack()

        content = tk.Frame(self.root, bg="#1E1E2E")
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        left = tk.Frame(content, bg="#1E1E2E")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        self._build_stat_card(left, "Temperature",  self.current_temp,     "C", "#F38BA8")
        self._build_stat_card(left, "Humidity",     self.current_humidity, "%", "#89DCEB")
        self._build_stat_card(left, "Setpoint",     self.current_setpoint, "C", "#A6E3A1")
        self._build_relay_card(left)
        self._build_alerts_panel(left)

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


def main():
    root = tk.Tk()
    app = SmartMattressGUI(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
