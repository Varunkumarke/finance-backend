from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import TokenResponse, UserRegisterRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user. Default role is 'viewer'.
    To assign analyst/admin roles, use the admin user-management endpoints.
    """
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with email + password. Returns a JWT bearer token.
    Use the token in the Authorization header: Bearer <token>
    """
    # OAuth2PasswordRequestForm uses 'username' field — we treat it as email
    return AuthService(db).login(email=form.username, password=form.password)
