"""
Run this once to create your first admin user.
Usage:  python create_admin.py
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

from app.database import SessionLocal
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import create_user

email = input("Admin email: ").strip()
password = getpass.getpass("Admin password (hidden): ")
name = input("Full name: ").strip()

db = SessionLocal()
try:
    user = create_user(db, UserCreate(email=email, password=password, full_name=name, role=UserRole.admin))
    print(f"\n✅  Admin created: {user.email} (id={user.id})")
finally:
    db.close()
