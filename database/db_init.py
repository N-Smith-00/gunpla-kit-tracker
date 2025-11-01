from config.config import DB_PATH
import sqlite3

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('PRAGMA journal_mode=WAL;')
    
    with open('database/schema.sql', 'r') as f:
        schema_sql = f.read()
    cur.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print("Database initialized")
    
if __name__ == '__main__':
    init_db()
