"""
CrowdIQ — Revoke Vote Use Case
"""
from __future__ import annotations

from src.application.port.output.vote_repository import AbstractVoteRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError


class RevokeVote:
    def __init__(self, vote_repo: AbstractVoteRepository) -> None:
        self._votes = vote_repo

    async def execute(self, vote_id: str, requester: User) -> None:
        vote = await self._votes.get_by_id(vote_id)
        if not vote:
            raise NotFoundError("Vote", vote_id)
        if vote.user_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("Cannot revoke another user's vote")
        await self._votes.delete(vote_id)
