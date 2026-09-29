from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.tree_service import get_tree_data

router = APIRouter()


@router.get("")
def get_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tree_data(db, current_user)
