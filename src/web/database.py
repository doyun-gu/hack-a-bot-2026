"""
GridBox — SQLite Database Layer
Persistent storage for sensor readings, fault events, and session stats.

Database file: src/web/gridbox.db (gitignored — data stays local)
Schema is auto-created on first run.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'gridbox.db')


def get_db():
    """Get database connection with row factory."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Create tables if they don't exist."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            bus_v REAL,
            m1_mA REAL,
            m2_mA REAL,
            m1_W REAL,
            m2_W REAL,
            total_W REAL,
            efficiency REAL,
            state TEXT,
            imu_rms REAL,
            imu_status TEXT,
            es_score REAL,
            m1_speed INTEGER,
            m2_speed INTEGER,
            mode INTEGER,
            total_items INTEGER,
            passed INTEGER,
            rejected INTEGER,
            reject_rate REAL,
            faults_today INTEGER
        );

        CREATE TABLE IF NOT EXISTS faults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            fault_type TEXT,
            source TEXT,
            imu_rms REAL,
            motor_current REAL,
            bus_voltage REAL,
            action_taken TEXT,
            resolved INTEGER DEFAULT 0,
            resolved_at TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            total_readings INTEGER DEFAULT 0,
            total_items_sorted INTEGER DEFAULT 0,
            total_passed INTEGER DEFAULT 0,
            total_rejected INTEGER DEFAULT 0,
            total_faults INTEGER DEFAULT 0,
            avg_power_W REAL,
            avg_efficiency REAL,
            dumb_power_W REAL,
            smart_power_W REAL,
            energy_saved_pct REAL
        );

        CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp);
        CREATE INDEX IF NOT EXISTS idx_faults_timestamp ON faults(timestamp);
    """)
    db.commit()
    db.close()
    print(f"[DB] Database ready: {DB_PATH}")


def insert_reading(data):
    """Insert a sensor reading from Pico serial data."""
    db = get_db()
    db.execute("""
        INSERT INTO readings (timestamp, bus_v, m1_mA, m2_mA, m1_W, m2_W,
            total_W, efficiency, state, imu_rms, imu_status, es_score,
            m1_speed, m2_speed, mode, total_items, passed, rejected,
            reject_rate, faults_today)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('timestamp', datetime.now().isoformat()),
        data.get('bus_v'), data.get('m1_mA'), data.get('m2_mA'),
        data.get('m1_W'), data.get('m2_W'), data.get('total_W'),
        data.get('efficiency'), data.get('state'),
        data.get('imu_rms'), data.get('imu_status'), data.get('es_score'),
        data.get('m1_speed'), data.get('m2_speed'), data.get('mode'),
        data.get('total_items'), data.get('passed'), data.get('rejected'),
        data.get('reject_rate'), data.get('faults_today'),
    ))
    db.commit()
    db.close()


def insert_fault(fault_type, source, imu_rms=None, motor_current=None,
                 bus_voltage=None, action_taken=None):
    """Log a fault event."""
    db = get_db()
    db.execute("""
        INSERT INTO faults (timestamp, fault_type, source, imu_rms,
            motor_current, bus_voltage, action_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(), fault_type, source,
        imu_rms, motor_current, bus_voltage, action_taken,
    ))
    db.commit()
    db.close()


def start_session():
    """Start a new monitoring session. Returns session ID."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO sessions (started_at) VALUES (?)",
        (datetime.now().isoformat(),)
    )
    session_id = cursor.lastrowid
    db.commit()
    db.close()
    return session_id


def end_session(session_id):
    """End a session and calculate summary stats."""
    db = get_db()
    session = db.execute(
        "SELECT started_at FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if session:
        started = session['started_at']
        stats = db.execute("""
            SELECT
                COUNT(*) as total_readings,
                MAX(total_items) as total_items_sorted,
                MAX(passed) as total_passed,
                MAX(rejected) as total_rejected,
                AVG(total_W) as avg_power_W,
                AVG(efficiency) as avg_efficiency
            FROM readings WHERE timestamp >= ?
        """, (started,)).fetchone()

        fault_count = db.execute(
            "SELECT COUNT(*) as cnt FROM faults WHERE timestamp >= ?",
            (started,)
        ).fetchone()['cnt']

        db.execute("""
            UPDATE sessions SET
                ended_at = ?,
                total_readings = ?,
                total_items_sorted = ?,
                total_passed = ?,
                total_rejected = ?,
                total_faults = ?,
                avg_power_W = ?,
                avg_efficiency = ?
            WHERE id = ?
        """, (
            datetime.now().isoformat(),
            stats['total_readings'],
            stats['total_items_sorted'] or 0,
            stats['total_passed'] or 0,
            stats['total_rejected'] or 0,
            fault_count,
            stats['avg_power_W'],
            stats['avg_efficiency'],
            session_id,
        ))
        db.commit()
    db.close()


def get_recent_readings(limit=300):
    """Get last N readings."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    db.close()
    return [dict(r) for r in reversed(rows)]


def get_recent_faults(limit=20):
    """Get last N fault events."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM faults ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    db.close()
    return [dict(r) for r in reversed(rows)]


def get_sessions(limit=10):
    """Get last N sessions with summaries."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    db.close()
    return [dict(r) for r in reversed(rows)]


def get_stats():
    """Get overall database statistics."""
    db = get_db()
    readings_count = db.execute("SELECT COUNT(*) as cnt FROM readings").fetchone()['cnt']
    faults_count = db.execute("SELECT COUNT(*) as cnt FROM faults").fetchone()['cnt']
    sessions_count = db.execute("SELECT COUNT(*) as cnt FROM sessions").fetchone()['cnt']

    latest = db.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()

    db.close()
    return {
        'total_readings': readings_count,
        'total_faults': faults_count,
        'total_sessions': sessions_count,
        'latest': dict(latest) if latest else None,
        'db_path': DB_PATH,
    }


if __name__ == "__main__":
    print("Initialising GridBox database...")
    init_db()
    stats = get_stats()
    print(f"Readings: {stats['total_readings']}")
    print(f"Faults: {stats['total_faults']}")
    print(f"Sessions: {stats['total_sessions']}")
    print(f"DB path: {stats['db_path']}")
