"""SQLite storage: users, prediction history, community posts and replies.

NOTE: on free hosts (like Streamlit Community Cloud) local files can be wiped
when the app restarts. For a real launch, move to a hosted database
(for example Supabase or Firebase).
"""
import datetime as dt
import hashlib
import hmac
import os
import shutil
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "data" / "app"
IMG_DIR = APP_DIR / "images"
DB_PATH = APP_DIR / "paddy.db"

ROLES = ["Farmer", "Agriculture expert / helper", "Buyer", "Input supplier"]
KINDS = ["Need help", "Offer help", "Sell produce", "Want to buy"]


def configure(app_dir):
    """Point the database at another folder (used by tests)."""
    global APP_DIR, IMG_DIR, DB_PATH
    APP_DIR = Path(app_dir)
    IMG_DIR = APP_DIR / "images"
    DB_PATH = APP_DIR / "paddy.db"


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def init():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT UNIQUE NOT NULL,
            phone TEXT, role TEXT NOT NULL, district TEXT, pw_hash TEXT NOT NULL,
            salt TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            label TEXT NOT NULL, confidence REAL NOT NULL, uncertain INTEGER NOT NULL,
            image TEXT, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL, district TEXT,
            share_phone INTEGER NOT NULL DEFAULT 0, image TEXT, diagnosis TEXT, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS replies(
            id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL, created TEXT NOT NULL);
        """)


# ---------- accounts ----------
def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()


def create_user(name, username, password, role, district="", phone=""):
    username = username.strip().lower()
    if len(name.strip()) < 2:
        return False, "Please enter your name."
    if len(username) < 3 or not username.replace("_", "").isalnum():
        return False, "Username must be at least 3 letters or numbers (underscore allowed)."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    salt = os.urandom(16)
    try:
        with conn() as c:
            c.execute("INSERT INTO users(name,username,phone,role,district,pw_hash,salt,created) VALUES(?,?,?,?,?,?,?,?)",
                      (name.strip(), username, phone.strip(), role, district.strip(), _hash(password, salt), salt.hex(), _now()))
    except sqlite3.IntegrityError:
        return False, "That username is taken. Try another one."
    return True, "Account created."


def authenticate(username, password):
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),)).fetchone()
    if not row:
        return None
    if not hmac.compare_digest(_hash(password, bytes.fromhex(row["salt"])), row["pw_hash"]):
        return None
    return {k: row[k] for k in ("id", "name", "username", "phone", "role", "district")}


def update_profile(user_id, district, phone):
    with conn() as c:
        c.execute("UPDATE users SET district=?, phone=? WHERE id=?", (district.strip(), phone.strip(), user_id))


# ---------- images ----------
def save_image(pil_image, max_side=800):
    img = pil_image.convert("RGB")
    img.thumbnail((max_side, max_side))
    name = f"{uuid.uuid4().hex}.jpg"
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(IMG_DIR / name, quality=85)
    return name


def copy_image(name):
    if not name:
        return None
    new = f"{uuid.uuid4().hex}.jpg"
    shutil.copy(IMG_DIR / name, IMG_DIR / new)
    return new


def image_path(name):
    return str(IMG_DIR / name) if name and (IMG_DIR / name).exists() else None


def _remove_image(name):
    if name:
        (IMG_DIR / name).unlink(missing_ok=True)


# ---------- history ----------
def add_prediction(user_id, label, confidence, uncertain, image_name):
    with conn() as c:
        cur = c.execute("INSERT INTO predictions(user_id,label,confidence,uncertain,image,created) VALUES(?,?,?,?,?,?)",
                        (user_id, label, float(confidence), int(bool(uncertain)), image_name, _now()))
        return cur.lastrowid


def list_predictions(user_id, label=None):
    q, a = "SELECT * FROM predictions WHERE user_id=?", [user_id]
    if label:
        q += " AND label=?"; a.append(label)
    with conn() as c:
        return c.execute(q + " ORDER BY id DESC", a).fetchall()


def delete_prediction(user_id, pred_id):
    with conn() as c:
        row = c.execute("SELECT image FROM predictions WHERE id=? AND user_id=?", (pred_id, user_id)).fetchone()
        if row:
            c.execute("DELETE FROM predictions WHERE id=?", (pred_id,))
    if row:
        _remove_image(row["image"])


# ---------- community ----------
def add_post(user_id, kind, title, body, district, share_phone, image_name=None, diagnosis=None):
    with conn() as c:
        cur = c.execute("INSERT INTO posts(user_id,kind,title,body,district,share_phone,image,diagnosis,created) VALUES(?,?,?,?,?,?,?,?,?)",
                        (user_id, kind, title.strip(), body.strip(), district.strip(), int(bool(share_phone)),
                         image_name, diagnosis, _now()))
        return cur.lastrowid


def list_posts(kind=None, district=None, user_id=None, limit=50):
    q = """SELECT p.*, u.name AS author, u.role AS author_role,
                  CASE WHEN p.share_phone=1 THEN u.phone END AS contact,
                  (SELECT COUNT(*) FROM replies r WHERE r.post_id=p.id) AS n_replies
           FROM posts p JOIN users u ON u.id=p.user_id WHERE 1=1"""
    a = []
    if kind:
        q += " AND p.kind=?"; a.append(kind)
    if district:
        q += " AND LOWER(p.district) LIKE ?"; a.append(f"%{district.strip().lower()}%")
    if user_id:
        q += " AND p.user_id=?"; a.append(user_id)
    with conn() as c:
        return c.execute(q + " ORDER BY p.id DESC LIMIT ?", a + [limit]).fetchall()


def delete_post(user_id, post_id):
    with conn() as c:
        row = c.execute("SELECT image FROM posts WHERE id=? AND user_id=?", (post_id, user_id)).fetchone()
        if row:
            c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    if row:
        _remove_image(row["image"])


def add_reply(post_id, user_id, body):
    with conn() as c:
        c.execute("INSERT INTO replies(post_id,user_id,body,created) VALUES(?,?,?,?)", (post_id, user_id, body.strip(), _now()))


def list_replies(post_id):
    with conn() as c:
        return c.execute("""SELECT r.*, u.name AS author, u.role AS author_role FROM replies r
                            JOIN users u ON u.id=r.user_id WHERE r.post_id=? ORDER BY r.id""", (post_id,)).fetchall()


def counts(user_id):
    with conn() as c:
        return (c.execute("SELECT COUNT(*) FROM predictions WHERE user_id=?", (user_id,)).fetchone()[0],
                c.execute("SELECT COUNT(*) FROM posts WHERE user_id=?", (user_id,)).fetchone()[0])


def time_ago(iso):
    s = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso)).total_seconds()
    if s < 60: return "just now"
    if s < 3600: return f"{int(s // 60)} min ago"
    if s < 86400: return f"{int(s // 3600)} h ago"
    if s < 86400 * 30: return f"{int(s // 86400)} d ago"
    return iso[:10]
