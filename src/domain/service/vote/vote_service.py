"""
CrowdIQ — Vote & Stake Service
"""
from __future__ import annotations

from typing import List

from src.application.dto.vote import CastVoteRequest, StakeRequest
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.model.vote import Vote
from src.application.port.output.vote_repository import AbstractVoteRepository
from src.domain.model.reputation import WalletTransaction
from src.application.port.output.reputation_repository import AbstractWalletRepository
from src.domain.exception.base import (
    AlreadyVotedError,
    InsufficientPointsError,
    NotFoundError,
    PredictionStatusError,
)
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class VoteService:
    def __init__(
        self,
        vote_repo: AbstractVoteRepository,
        prediction_repo: AbstractPredictionRepository,
        user_repo: AbstractUserRepository,
        wallet_repo: AbstractWalletRepository,
    ) -> None:
        self._votes = vote_repo
        self._predictions = prediction_repo
        self._users = user_repo
        self._wallet = wallet_repo

    async def cast_vote(self, prediction_id: str, req: CastVoteRequest, voter: User) -> Vote:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        if not pred.can_vote():
            raise PredictionStatusError("vote on", pred.status.value)

        # enforce one-vote-per-user
        existing = await self._votes.get_by_user_and_prediction(voter.id, prediction_id)
        if existing:
            raise AlreadyVotedError()

        # validate option belongs to prediction
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

    async def stake_points(self, prediction_id: str, req: StakeRequest, voter: User) -> Vote:
        existing = await self._votes.get_by_user_and_prediction(voter.id, prediction_id)
        if not existing:
            raise NotFoundError("Vote", f"user={voter.id} prediction={prediction_id}")

        if voter.virtual_points < req.amount:
            raise InsufficientPointsError(req.amount, voter.virtual_points)

        # debit wallet
        voter.virtual_points -= req.amount
        voter.updated_at = utc_now()
        await self._users.update(voter)

        await self._wallet.add_transaction(
            WalletTransaction(
                id=generate_uuid(),
                user_id=voter.id,
                amount=-req.amount,
                reason=f"Stake on prediction {prediction_id}",
                prediction_id=prediction_id,
                created_at=utc_now(),
            )
        )
        return await self._votes.update_stake(existing.id, existing.stake + req.amount)

    async def get_votes_for_prediction(
        self, prediction_id: str, skip: int, limit: int
    ) -> List[Vote]:
        return await self._votes.get_by_prediction(prediction_id, skip, limit)

    async def get_votes_for_user(self, user_id: str, skip: int, limit: int) -> List[Vote]:
        return await self._votes.get_by_user(user_id, skip, limit)
