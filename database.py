import sqlite3
from datetime import datetime

DB_NAME = "student_support.db"

def init_db():
    """Initializes the SQLite database and creates the check-in table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create the check_ins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sleep_hours REAL,
            mood_score INTEGER,          -- e.g., 1-10
            energy_level INTEGER,        -- e.g., 1-10
            workload_level INTEGER,      -- e.g., 1-10
            academic_pressure INTEGER,   -- e.g., 1-10
            deadlines_count INTEGER,
            optional_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()