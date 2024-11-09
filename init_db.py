import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('university_schedule.db')
cursor = conn.cursor()

# Create the `course_schedule` table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT NOT NULL,
        course_code TEXT NOT NULL,
        course_title TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        class_start_time TIME NOT NULL,
        class_end_time TIME NOT NULL,
        room INTEGER NOT NULL
    )
''')

conn.commit()
conn.close()
print("Database and table created successfully.")
