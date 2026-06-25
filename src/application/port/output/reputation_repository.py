"""
CrowdIQ — Reputation & Wallet Repository Ports
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from src.domain.model.reputation import ReputationHistory, WalletTransaction


class AbstractReputationRepository(ABC):
    @abstractmethod
    async def add_history(self, entry: ReputationHistory) -> ReputationHistory: ...

    @abstractmethod
    async def get_history(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[ReputationHistory]: ...


class AbstractWalletRepository(ABC):
    @abstractmethod
    async def add_transaction(self, tx: WalletTransaction) -> WalletTransaction: ...

    @abstractmethod
    async def get_history(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[WalletTransaction]: ...
