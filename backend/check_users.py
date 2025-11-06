import sqlite3

conn = sqlite3.connect('climate_health.db')
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone()

if table_exists:
    cursor.execute('SELECT id, email, role, full_name FROM users')
    users = cursor.fetchall()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, Name: {user[3]}")
else:
    print("Users table does not exist!")

conn.close()
