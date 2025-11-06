import sqlite3
from app.auth.auth import verify_password, get_password_hash

conn = sqlite3.connect('climate_health.db')
cursor = conn.cursor()

# Get admin user
cursor.execute('SELECT email, hashed_password FROM users WHERE email = ?', ('admin@climate-health.org',))
admin = cursor.fetchone()

if admin:
    email, hashed = admin
    print(f"Admin user found: {email}")
    print(f"Stored hash: {hashed[:50]}...")
    
    # Test password
    test_password = "admin123"
    result = verify_password(test_password, hashed)
    print(f"\nPassword 'admin123' verification: {result}")
    
    # Generate new hash for comparison
    new_hash = get_password_hash(test_password)
    print(f"\nNew hash for 'admin123': {new_hash[:50]}...")
else:
    print("Admin user not found!")

conn.close()
