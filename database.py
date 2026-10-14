"""SQLite storage (users + history) with admin queries"""
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "resumes.db")  # always next to the code, whatever folder the app is started from
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@resume.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def _now():
    return datetime.now().strftime("%d-%m-%Y %H:%M")


def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            role TEXT NOT NULL, created TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, filename TEXT, score REAL, matched TEXT, missing TEXT, created TEXT,
            stored_file TEXT, jd TEXT, FOREIGN KEY(user_id) REFERENCES users(id))""")
        # upgrade older databases
        cols = [r[1] for r in c.execute("PRAGMA table_info(history)")]
        for col, typ in (("user_id", "INTEGER"), ("stored_file", "TEXT"), ("jd", "TEXT")):
            if col not in cols:
                c.execute(f"ALTER TABLE history ADD COLUMN {col} {typ}")
        # default admin account
        if not c.execute("SELECT 1 FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
            c.execute("INSERT INTO users(name,email,password_hash,role,created) VALUES(?,?,?,?,?)",
                      ("Administrator", ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD), "Admin", _now()))


# ---------------- users ----------------
def create_user(name, email, password_hash, role):
    """Returns True if created, False if email already exists."""
    try:
        with _conn() as c:
            c.execute("INSERT INTO users(name,email,password_hash,role,created) VALUES(?,?,?,?,?)",
                      (name, email, password_hash, role, _now()))
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_email(email):
    with _conn() as c:
        return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()


# ---------------- history (normal user) ----------------
def save_result(user_id, filename, score, matched, missing, stored_file, jd):
    """Save one analysis and return its id."""
    with _conn() as c:
        cur = c.execute("INSERT INTO history(user_id,filename,score,matched,missing,created,stored_file,jd) "
                        "VALUES(?,?,?,?,?,?,?,?)",
                        (user_id, filename, score, ", ".join(matched), ", ".join(missing), _now(), stored_file, jd))
        return cur.lastrowid


def get_user_record(user_id, record_id):
    """One analysis of this user (None if it belongs to somebody else)."""
    with _conn() as c:
        return c.execute("SELECT * FROM history WHERE id=? AND user_id=?", (record_id, user_id)).fetchone()


def get_history(user_id):
    with _conn() as c:
        return c.execute("SELECT filename,score,matched,missing,created FROM history "
                         "WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()


# ---------------- admin dashboard ----------------
def get_stats():
    with _conn() as c:
        users = c.execute("SELECT COUNT(*) FROM users WHERE role!='Admin'").fetchone()[0]
        n, avg = c.execute("SELECT COUNT(*), AVG(score) FROM history WHERE user_id IN "
                           "(SELECT id FROM users WHERE role!='Admin')").fetchone()
        return {"users": users, "resumes": n, "avg": round(avg or 0)}


def get_users_with_stats():
    with _conn() as c:
        return c.execute("""SELECT u.id, u.name, u.email, u.role, COUNT(h.id) AS resumes,
            (SELECT created FROM history WHERE user_id=u.id ORDER BY id DESC LIMIT 1) AS last_active
            FROM users u LEFT JOIN history h ON h.user_id=u.id WHERE u.role!='Admin'
            GROUP BY u.id ORDER BY COALESCE(MAX(h.id),0) DESC, u.id DESC""").fetchall()


def get_user(user_id):
    with _conn() as c:
        return c.execute("SELECT * FROM users WHERE id=? AND role!='Admin'", (user_id,)).fetchone()


def get_user_records(user_id):
    with _conn() as c:
        return c.execute("SELECT id,filename,score,created FROM history WHERE user_id=? ORDER BY id DESC",
                         (user_id,)).fetchall()


def get_record(record_id):
    with _conn() as c:
        return c.execute("""SELECT h.*, u.name AS user_name, u.role AS user_role
            FROM history h JOIN users u ON u.id=h.user_id WHERE h.id=? AND u.role!='Admin'""",
                         (record_id,)).fetchone()
