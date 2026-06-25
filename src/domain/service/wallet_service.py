"""
CrowdIQ — Wallet Service
"""
from __future__ import annotations

from typing import List

from src.domain.model.reputation import WalletTransaction
from src.application.port.output.reputation_repository import AbstractWalletRepository
from src.domain.model.user import User


class WalletService:
    def __init__(self, wallet_repo: AbstractWalletRepository) -> None:
        self._wallet = wallet_repo

    async def get_balance(self, user: User) -> dict:
        return {"user_id": user.id, "virtual_points": user.virtual_points}

    async def get_history(
        self, user: User, skip: int, limit: int
    ) -> List[WalletTransaction]:
        return await self._wallet.get_history(user.id, skip, limit)
