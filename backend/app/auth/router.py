"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.schemas.response import success_response
from app.schemas.user import UserResponse
from app.schemas.workspace import WorkspaceResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(get_db)
) -> dict:
    user, workspace, token = await AuthService(session).register(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    data = RegisterResponse(
        user=UserResponse.model_validate(user),
        workspace=WorkspaceResponse.model_validate(workspace),
        token=token,
    )
    return success_response(
        data=data.model_dump(mode="json"),
        message="Registration successful",
    )


@router.post("/login")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> dict:
    _, token = await AuthService(session).login(
        email=payload.email, password=payload.password
    )
    return success_response(
        data=TokenResponse.model_validate(token).model_dump(mode="json"),
        message="Login successful",
    )


@router.get("/me")
async def current_user(user: User = Depends(get_current_user)) -> dict:
    return success_response(
        data=UserResponse.model_validate(user).model_dump(mode="json"),
        message="OK",
    )
