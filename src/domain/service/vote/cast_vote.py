"""
CrowdIQ — Cast Vote Use Case
"""
from __future__ import annotations

from src.application.dto.vote import CastVoteRequest
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.model.vote import Vote
from src.application.port.output.vote_repository import AbstractVoteRepository
from src.domain.exception.base import (
    AlreadyVotedError,
    NotFoundError,
    PredictionStatusError,
)
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class CastVote:
    def __init__(
        self,
        vote_repo: AbstractVoteRepository,
        prediction_repo: AbstractPredictionRepository,
    ) -> None:
        self._votes = vote_repo
        self._predictions = prediction_repo

    async def execute(
        self, prediction_id: str, req: CastVoteRequest, voter: User
    ) -> Vote:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        if not pred.can_vote():
            raise PredictionStatusError("vote on", pred.status.value)

        existing = await self._votes.get_by_user_and_prediction(voter.id, prediction_id)
        if existing:
            raise AlreadyVotedError()

        valid_ids = {o.id for o in pred.options}
        if req.option_id not in valid_ids:
            raise NotFoundError("Option", req.option_id)

        vote = Vote(
            id=generate_uuid(),
            user_id=voter.id,
            prediction_id=prediction_id,
            option_id=req.option_id,
            confidence=req.confidence,
            created_at=utc_now(),
        )
        return await self._votes.create(vote)
