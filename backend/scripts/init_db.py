#!/usr/bin/env python3
"""
Initialize database and create admin user.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import init_db, SessionLocal
from models import AdminConfig
from services.auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Initializing database...")

    # Create all tables
    init_db()
    print("✓ Database tables created")

    # Create admin user
    db = SessionLocal()
    try:
        admin = db.query(AdminConfig).filter(AdminConfig.id == 1).first()

        if not admin:
            default_password = os.getenv("ADMIN_PASSWORD", "admin123")
            password_hash = get_password_hash(default_password)

            admin = AdminConfig(
                id=1,
                password_hash=password_hash
            )
            db.add(admin)
            db.commit()

            print(f"✓ Admin user created with password: {default_password}")
            print("⚠️  IMPORTANT: Change this password in production!")
        else:
            print("✓ Admin user already exists")

    finally:
        db.close()

    print("\n✓ Database initialization complete!")
    print("\nNext steps:")
    print("1. Update .env with secure passwords")
    print("2. Run: uvicorn main:app --reload")
    print("3. Visit: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
