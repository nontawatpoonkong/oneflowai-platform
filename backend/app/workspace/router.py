"""Workspace routes.

NOTE: A standalone "Create Workspace" endpoint is part of the overall
Sprint 1 scope. It is not in Step 2's explicit requirement list, so it is
included here as a convenience but flagged for your review — say the word
and it can be deferred to a later step.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.response import success_response
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceResponse
from app.services.workspace import WorkspaceService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    workspace = await WorkspaceService(session).create_workspace(
        owner_id=user.id, name=payload.name
    )
    return success_response(
        data=WorkspaceResponse.model_validate(workspace).model_dump(mode="json"),
        message="Workspace created",
    )
