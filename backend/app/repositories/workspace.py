"""Workspace repository."""

from sqlalchemy import select

from app.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace

    async def slug_exists(self, slug: str) -> bool:
        result = await self.session.execute(
            select(Workspace.id).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none() is not None
