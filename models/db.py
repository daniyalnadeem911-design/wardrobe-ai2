import os
from config import Config
import turso_serverless   # was: import libsql

def get_connection():
    conn = turso_serverless.connect(
        Config.TURSO_DATABASE_URL,
        auth_token=Config.TURSO_AUTH_TOKEN,
    )
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    with open(os.path.join("database", "schema.sql"), "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def _row_to_dict(cur, row):
    columns = [d[0] for d in cur.description]
    return dict(zip(columns, row))

def query(sql, params=(), fetchone=False, commit=False):
    conn = get_connection()
    cur = conn.execute(sql, params)
    result = None
    if commit:
        conn.commit()
        result = cur.lastrowid
    elif fetchone:
        row = cur.fetchone()
        result = _row_to_dict(cur, row) if row else None
    else:
        rows = cur.fetchall()
        result = [_row_to_dict(cur, r) for r in rows] if rows else []
    conn.close()
    return result