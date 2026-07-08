"""
CrowdIQ — Wallet Domain Model
Pure Python dataclass; zero infrastructure dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Wallet:
    """Represents a user's virtual-points ledger."""
    user_id: str
    balance: int = 1000

    def credit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        self.balance += amount

    def debit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        if self.balance < amount:
            raise ValueError(f"Insufficient balance: have {self.balance}, need {amount}")
        self.balance -= amount
