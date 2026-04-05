from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_active_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_active_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    """
    List all users. Admin only.
    """
    return UserService(db).get_all_users()


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID. Admin only.
    """
    return UserService(db).get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: int, data: UserUpdateRequest, db: Session = Depends(get_db)):
    """
    Update a user's name, role, or active status. Admin only.
    This is how you promote a viewer to analyst or admin.
    """
    return UserService(db).update_user(user_id, data)


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Deactivate a user account. Admin only.
    Cannot deactivate your own account.
    """
    return UserService(db).deactivate_user(user_id, requesting_user=current_user)
