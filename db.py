"""
db.py — SQLite data layer for Smart Data Management System (SaaS-style)
Handles: users, auth tokens (persistent login), uploaded file history (per-user).
"""

import sqlite3
import hashlib
import secrets
import os
import io
from datetime import datetime, timedelta
from contextlib import contextmanager

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sdms.db")


# ──────────────────────────────────────────────────────────────────────────
# CONNECTION
# ──────────────────────────────────────────────────────────────────────────
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                rows INTEGER,
                cols INTEGER,
                file_blob BLOB NOT NULL,
                file_type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


# ──────────────────────────────────────────────────────────────────────────
# PASSWORD HASHING (PBKDF2 — no extra system deps needed)
# ──────────────────────────────────────────────────────────────────────────
def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()


def _make_salt() -> str:
    return secrets.token_hex(16)


# ──────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────
def username_exists(username: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()
        return row is not None


def create_user(username: str, password: str, full_name: str = "", email: str = "") -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Username এবং Password দিতে হবে।"
    if len(username) < 3:
        return False, "Username কমপক্ষে ৩ অক্ষরের হতে হবে।"
    if len(password) < 4:
        return False, "Password কমপক্ষে ৪ অক্ষরের হতে হবে।"
    if username_exists(username):
        return False, "এই Username আগেই ব্যবহৃত হয়েছে।"

    salt = _make_salt()
    pw_hash = _hash_password(password, salt)
    now = datetime.utcnow().isoformat()

    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO users (username, full_name, email, password_hash, salt, role, created_at)
                   VALUES (?, ?, ?, ?, ?, 'user', ?)""",
                (username, full_name.strip(), email.strip(), pw_hash, salt, now),
            )
        log_activity(None, username, "signup", "নতুন একাউন্ট তৈরি হয়েছে")
        return True, "একাউন্ট সফলভাবে তৈরি হয়েছে! এখন লগইন করুন।"
    except sqlite3.IntegrityError:
        return False, "এই Username আগেই ব্যবহৃত হয়েছে।"


def verify_user(username: str, password: str):
    """Returns user row dict if valid, else None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username.strip(),)
        ).fetchone()
        if row is None:
            return None
        expected = _hash_password(password, row["salt"])
        if secrets.compare_digest(expected, row["password_hash"]):
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), row["id"]),
            )
            return dict(row)
        return None


def get_user_by_id(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_all_users():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT u.id, u.username, u.full_name, u.email, u.role, u.created_at, u.last_login,
                      (SELECT COUNT(*) FROM files f WHERE f.user_id = u.id) AS file_count
               FROM users u ORDER BY u.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────
# SESSION TOKENS (for "stay logged in" persistence via cookie)
# ──────────────────────────────────────────────────────────────────────────
def create_session(user_id: int, days_valid: int = 14) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    expires = now + timedelta(days=days_valid)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now.isoformat(), expires.isoformat()),
        )
    return token


def get_user_by_session(token: str):
    if not token:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None
        user = conn.execute("SELECT * FROM users WHERE id = ?", (row["user_id"],)).fetchone()
        return dict(user) if user else None


def delete_session(token: str):
    if not token:
        return
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


# ──────────────────────────────────────────────────────────────────────────
# FILE HISTORY (per-user, persisted as blobs so re-login restores everything)
# ──────────────────────────────────────────────────────────────────────────
def save_file(user_id: int, file_name: str, raw_bytes: bytes, file_type: str, rows: int, cols: int) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO files (user_id, file_name, uploaded_at, rows, cols, file_blob, file_type)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, file_name, now, rows, cols, raw_bytes, file_type),
        )
        return cur.lastrowid


def get_user_files(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, file_name, uploaded_at, rows, cols, file_type
               FROM files WHERE user_id = ? ORDER BY uploaded_at DESC""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_file_dataframe(file_id: int, user_id: int):
    """Loads a previously uploaded file back into a DataFrame. Scoped to user_id for safety."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)
        ).fetchone()
        if row is None:
            return None, None
        blob = row["file_blob"]
        if row["file_type"] == "csv":
            df = pd.read_csv(io.BytesIO(blob))
        else:
            df = pd.read_excel(io.BytesIO(blob))
        return df, row["file_name"]


def delete_file(file_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))


def get_all_files_admin():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT f.id, f.file_name, f.uploaded_at, f.rows, f.cols, f.file_type,
                      u.username
               FROM files f JOIN users u ON u.id = f.user_id
               ORDER BY f.uploaded_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────
# ACTIVITY LOG (admin can see who did what, when)
# ──────────────────────────────────────────────────────────────────────────
def log_activity(user_id, username, action, detail=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO activity_log (user_id, username, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, action, detail, datetime.utcnow().isoformat()),
        )


def get_recent_activity(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────
# STATS for admin dashboard
# ──────────────────────────────────────────────────────────────────────────
def get_admin_stats():
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) c FROM users WHERE role='user'").fetchone()["c"]
        total_files = conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"]
        today = datetime.utcnow().date().isoformat()
        signups_today = conn.execute(
            "SELECT COUNT(*) c FROM users WHERE role='user' AND created_at LIKE ?", (today + "%",)
        ).fetchone()["c"]
        uploads_today = conn.execute(
            "SELECT COUNT(*) c FROM files WHERE uploaded_at LIKE ?", (today + "%",)
        ).fetchone()["c"]
        return {
            "total_users": total_users,
            "total_files": total_files,
            "signups_today": signups_today,
            "uploads_today": uploads_today,
        }