from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    """
    Handles user management operations.
    Only admins can reach most of these via the route layer.
    """

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_all_users(self) -> list[UserResponse]:
        users = self.repo.get_all()
        return [UserResponse.model_validate(u) for u in users]

    def get_user(self, user_id: int) -> UserResponse:
        user = self._get_or_404(user_id)
        return UserResponse.model_validate(user)

    def update_user(self, user_id: int, data: UserUpdateRequest) -> UserResponse:
        user = self._get_or_404(user_id)
        updates = data.model_dump(exclude_none=True)
        updated = self.repo.update(user, **updates)
        return UserResponse.model_validate(updated)

    def deactivate_user(self, user_id: int, requesting_user: User) -> UserResponse:
        if user_id == requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account",
            )
        user = self._get_or_404(user_id)
        updated = self.repo.update(user, is_active=False)
        return UserResponse.model_validate(updated)

    def _get_or_404(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user
