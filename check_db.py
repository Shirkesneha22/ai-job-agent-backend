import sqlite3
try:
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(jobs);")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
