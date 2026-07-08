"""
CrowdIQ — Award Points Use Case
"""
from __future__ import annotations

from src.domain.model.reputation import WalletTransaction
from src.application.port.output.reputation_repository import AbstractWalletRepository
from src.domain.model.user import User
from src.application.port.output.user_repository import AbstractUserRepository
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class AwardPoints:
    def __init__(
        self,
        wallet_repo: AbstractWalletRepository,
        user_repo: AbstractUserRepository,
    ) -> None:
        self._wallet = wallet_repo
        self._users = user_repo

    async def execute(self, user: User, amount: int, reason: str) -> None:
        user.virtual_points += amount
        user.updated_at = utc_now()
        await self._users.update(user)
        await self._wallet.add_transaction(
            WalletTransaction(
                id=generate_uuid(),
                user_id=user.id,
                amount=amount,
                reason=reason,
                created_at=utc_now(),
            )
        )
