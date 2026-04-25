"""
CRM 360 — Create Users Table & Add Login Credentials
Run this ONCE: python create_users.py
"""

from db import get_connection

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            dept VARCHAR(50)
        )
    """)

    # Clear existing users (if re-running)
    cursor.execute("TRUNCATE TABLE users")

    # Insert users: Admin + Support Agents
    users = [
        ('admin',  'admin123',  'Admin User',     'Admin',  'admin@crm360.io',    'Management'),
        ('arjun',  'agent123',  'Arjun Mehta',    'Agent',  'arjun@crm.com',      'Technical'),
        ('priya',  'agent123',  'Priya Nair',     'Agent',  'priya.n@crm.com',    'Customer Service'),
        ('ritika', 'agent123',  'Ritika Sharma',  'Agent',  'ritika@crm.com',     'Order Support'),
        ('manoj',  'agent123',  'Manoj Kumar',    'Agent',  'manoj@crm.com',      'Returns'),
    ]

    cursor.executemany("""
        INSERT INTO users (username, password, full_name, role, email, dept)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, users)

    conn.commit()
    conn.close()

    print("=" * 50)
    print("  USERS TABLE CREATED SUCCESSFULLY!")
    print("=" * 50)
    print("  Login credentials:")
    print("  ----------------------------------")
    print("  admin  / admin123   (Admin - full access)")
    print("  arjun  / agent123   (Agent)")
    print("  priya  / agent123   (Agent)")
    print("  ritika / agent123   (Agent)")
    print("  manoj  / agent123   (Agent)")
    print("=" * 50)

if __name__ == '__main__':
    create_users_table()
