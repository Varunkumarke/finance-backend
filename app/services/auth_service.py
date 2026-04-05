from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserRegisterRequest, UserResponse


class AuthService:
    """
    Handles user registration and login.
    Keeps auth logic separate from the route layer.
    """

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserRegisterRequest) -> UserResponse:
        if self.repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        user = self.repo.create(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return UserResponse.model_validate(user)

    def login(self, email: str, password: str) -> TokenResponse:
        user: User | None = self.repo.get_by_email(email)

        # Use a generic error to avoid leaking whether the email exists
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated",
            )

        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
