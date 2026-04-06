import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exercise_type TEXT,
        repetitions INTEGER,
        score INTEGER,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()