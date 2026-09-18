import sqlite3
import bcrypt

DB_PATH = "products.db"


def create_users_table():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def register_user(full_name, email, password):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    )

    if cur.fetchone():
        conn.close()
        return False, "Email already exists."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cur.execute("""
        INSERT INTO users (
            full_name,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
    """, (
        full_name,
        email,
        password_hash
    ))

    conn.commit()
    conn.close()

    return True, "Account created successfully."


def login_user(email, password):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            full_name,
            email,
            password_hash
        FROM users
        WHERE email = ?
    """, (email,))

    user = cur.fetchone()

    conn.close()

    if not user:
        return None

    if bcrypt.checkpw(
        password.encode("utf-8"),
        user[3].encode("utf-8")
    ):

        return {
            "id": user[0],
            "full_name": user[1],
            "email": user[2]
        }

    return None