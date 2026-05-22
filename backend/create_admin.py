"""
Run this once to create your first admin user.
Usage:  python create_admin.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.models.user import UserRole

email = input("Admin email: ").strip()
password = input("Admin password: ").strip()
name = input("Full name: ").strip()

db = SessionLocal()
try:
    user = create_user(db, UserCreate(email=email, password=password, full_name=name, role=UserRole.admin))
    print(f"\n✅  Admin created: {user.email} (id={user.id})")
finally:
    db.close()
