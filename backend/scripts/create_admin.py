"""
Script to create the first super admin user.
Run from the backend directory:
    python scripts/create_admin.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.utils.security import hash_password
from datetime import datetime

# Create all tables
Base.metadata.create_all(bind=engine)

def create_super_admin(email: str, password: str, full_name: str):
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"Admin with email '{email}' already exists.")
            return

        admin = AdminUser(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role="super_admin",
            permissions=["create_admin", "update_admin", "delete_admin", "approve_application", "view_analytics"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        print(f"✅ Super admin created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: super_admin")
        print(f"\nLogin at: http://localhost:5173/admin/login")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin(
        email="admin@creditscoring.com",
        password="Admin@123456",
        full_name="Super Admin"
    )
