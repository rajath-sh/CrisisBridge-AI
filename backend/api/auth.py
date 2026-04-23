"""
Auth API Routes for CrisisBridge AI
====================================
Endpoints:
- POST /register
- POST /login
- GET /me
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from shared.dependencies import get_db, get_current_active_user
from shared.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from shared.models import User
from backend.services import auth as auth_service

router = APIRouter()


@router.post(
    "/register", 
    response_model=TokenResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_data: UserRegister, 
    db: Session = Depends(get_db)
):
    """
    Registers a new user and returns an access token.
    Default role is 'guest'.
    """
    user = auth_service.register_user(db, user_data)
    return auth_service.get_token_response(user)


@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Login and get access token"
)
async def login(
    login_data: UserLogin, 
    db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.
    """
    user = auth_service.authenticate_user(db, login_data)
    return auth_service.get_token_response(user)


@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns the profile of the currently authenticated user.
    """
    return UserResponse.from_orm(current_user)
