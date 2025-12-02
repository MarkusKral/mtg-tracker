#!/usr/bin/env python3
"""
Reset admin password to default (admin123) or custom password.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import SessionLocal
from models import AdminConfig
from services.auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()


def main():
    print("=" * 60)
    print("Admin Password Reset Tool")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        admin = db.query(AdminConfig).filter(AdminConfig.id == 1).first()
        
        if not admin:
            print("\nAdmin user not found in database!")
            print("Creating admin user...")
            default_password = os.getenv("ADMIN_PASSWORD", "admin123")
            password_hash = get_password_hash(default_password)
            
            admin = AdminConfig(
                id=1,
                password_hash=password_hash
            )
            db.add(admin)
            db.commit()
            print("Admin user created with password: " + default_password)
        else:
            print("\nAdmin user found")
            
            # Ask for new password
            new_password = input("\nEnter new password (or press Enter for 'admin123'): ").strip()
            if not new_password:
                new_password = "admin123"
            
            # Update password
            admin.password_hash = get_password_hash(new_password)
            db.commit()
            print("\nAdmin password updated to: " + new_password)
        
        print("\n" + "=" * 60)
        print("You can now login with the new password")
        print("=" * 60)
        
    except Exception as e:
        print("\nError: " + str(e))
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
