"""Authentication dependencies."""

import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import context
from app.core.exceptions import AuthenticationError, InactiveUserError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.services.auth import AuthService

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationError("Missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Invalid token") from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Invalid token payload")

    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise AuthenticationError("Invalid token subject") from exc

    user = await AuthService(session).get_user_by_id(user_id)
    if not user.is_active:
        raise InactiveUserError()

    # Populate logging context for the remainder of the request.
    context.set_user_id(str(user.id))
    return user
