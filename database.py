"""
database.py
Handles all raw SQL / SQLite database access for the HRMS application.
No ORM is used -- plain Python sqlite3 + hand-written SQL, per assignment
requirements (Database: python SQL, no MySQL server).
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "hrms.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset=False):
    """Create tables (and seed a default HR account) if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    fresh = reset or not os.path.exists(DB_PATH)

    conn = get_db()
    if fresh:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        conn.commit()
        seed_default_hr(conn)
    conn.close()


def seed_default_hr(conn):
    """Create a default HR login so the app is usable immediately."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", ("hr@zeerostock.com",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            ("hr@zeerostock.com", generate_password_hash("HrAdmin@123"), "HR"),
        )
        conn.commit()


if __name__ == "__main__":
    init_db(reset=True)
    print(f"Initialized database at {DB_PATH}")
    print("Default HR login -> email: hr@zeerostock.com  password: HrAdmin@123")
