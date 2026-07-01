"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse
from app.schemas.workspace import WorkspaceResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RegisterResponse(BaseModel):
    user: UserResponse
    workspace: WorkspaceResponse
    token: TokenResponse
