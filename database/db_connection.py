from config.config import DB_PATH
import sqlite3

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

from contextlib import contextmanager

@contextmanager
def connection():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback
        raise
    finally:
        conn.close()