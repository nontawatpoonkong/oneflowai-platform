"""WorkspaceMember repository."""

from app.models.workspace_member import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    model = WorkspaceMember
