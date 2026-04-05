from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    """
    Handles all database interactions for User records.
    Keeps raw SQL/ORM logic out of the service layer.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 50) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, name: str, email: str, hashed_password: str, role: UserRole = UserRole.viewer) -> User:
        user = User(name=name, email=email, hashed_password=hashed_password, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **kwargs) -> User:
        for field, value in kwargs.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def email_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None
