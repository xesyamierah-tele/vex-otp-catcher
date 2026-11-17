import sqlite3
from pathlib import Path
import os

DB_PATH = os.getenv("DATABASE_PATH", "bot.sqlite3")

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            added_by INTEGER NOT NULL
        )""")

def is_authorized(user_id: int) -> bool:
    from config import OWNER_ID
    if user_id == OWNER_ID:
        return True
    with connect() as db:
        row = db.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
    return row is not None

def add_admin_record(user_id: int, added_by: int):
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO admins(user_id, added_by) VALUES (?, ?)",
                   (user_id, added_by))

def remove_admin_record(user_id: int):
    from config import OWNER_ID
    if user_id == OWNER_ID:
        raise ValueError("The owner cannot be removed.")
    with connect() as db:
        db.execute("DELETE FROM admins WHERE user_id=?", (user_id,))

def get_admin_ids():
    with connect() as db:
        return [row[0] for row in db.execute("SELECT user_id FROM admins ORDER BY user_id")]
