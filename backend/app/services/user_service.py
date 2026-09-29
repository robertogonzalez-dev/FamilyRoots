from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRegister, UserUpdate


def create_user(db: Session, data: UserCreate) -> User:
    email = data.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_user(db: Session, data: UserRegister) -> User:
    """Self-registration always creates a viewer."""
    email = data.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.viewer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
    if not user:
        return None
    valid, upgraded_hash = verify_password(password, user.password_hash)
    if not valid or not user.is_active:
        return None
    if upgraded_hash:  # transparently move legacy bcrypt hashes to Argon2
        user.password_hash = upgraded_hash
        db.commit()
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def get_first_admin(db: Session) -> User | None:
    return db.query(User).filter(User.role == UserRole.admin).first()
