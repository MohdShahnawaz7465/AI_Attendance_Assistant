import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll_no TEXT,
    present_days INTEGER,
    total_days INTEGER
)
""")

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create email_settings table (NEW - for email alerts)
cursor.execute("""
CREATE TABLE IF NOT EXISTS email_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_enabled BOOLEAN DEFAULT 0,
    sender_email TEXT,
    smtp_server TEXT,
    smtp_port INTEGER
)
""")

# Insert sample students
students = [
    ("Ali", "101", 70, 90),
    ("Mohd Shahnawaz", "102", 60, 90),
    ("Kashif", "103", 85, 90)
]

cursor.executemany(
    "INSERT INTO students(name, roll_no, present_days, total_days) VALUES (?, ?, ?, ?)",
    students
)

# Insert demo user
cursor.execute(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    ("admin", "admin123")
)

conn.commit()
conn.close()

print("✅ Database Created Successfully!")
print("📋 Tables: students, users, email_settings")
print("👤 Sample students: 3")
print("🔐 Demo user: admin / admin123")