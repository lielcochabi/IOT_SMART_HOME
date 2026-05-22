import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mattress.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS setpoint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            setpoint REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")


def insert_temperature(temperature, humidity):
    conn = get_connection()
    conn.execute(
        "INSERT INTO temperature_log (temperature, humidity) VALUES (?, ?)",
        (temperature, humidity)
    )
    conn.commit()
    conn.close()


def insert_setpoint(setpoint):
    conn = get_connection()
    conn.execute(
        "INSERT INTO setpoint_history (setpoint) VALUES (?)",
        (setpoint,)
    )
    conn.commit()
    conn.close()


def insert_alert(level, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO alerts (level, message) VALUES (?, ?)",
        (level, message)
    )
    conn.commit()
    conn.close()


def get_recent_temperatures(limit=100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT timestamp, temperature, humidity FROM temperature_log ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows


def get_recent_alerts(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT timestamp, level, message FROM alerts ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows


def get_recent_setpoints(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT timestamp, setpoint FROM setpoint_history ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
