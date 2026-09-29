from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.person import Person
from app.models.relationship import Relationship
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import create_user, update_user

router = APIRouter()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return {
        "total_people": db.query(Person).count(),
        "total_relationships": db.query(Relationship).count(),
        "total_users": db.query(User).count(),
        "living_people": db.query(Person).filter(Person.is_living.is_(True)).count(),
    }


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).all()


@router.post("/users", response_model=UserResponse, status_code=201)
def admin_create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return create_user(db, data)


@router.patch("/users/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id and (
        (data.role is not None and data.role != UserRole.admin) or data.is_active is False
    ):
        raise HTTPException(status_code=400, detail="You cannot demote or deactivate yourself")
    return update_user(db, user, data)


@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
