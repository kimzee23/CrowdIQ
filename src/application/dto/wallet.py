"""
CrowdIQ — Wallet DTOs
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WalletResponse(BaseModel):
    user_id: str
    virtual_points: int


class WalletTransactionResponse(BaseModel):
    id: str
    user_id: str
    amount: int
    reason: str
    prediction_id: Optional[str]
    created_at: datetime


class WalletHistoryResponse(BaseModel):
    transactions: List[WalletTransactionResponse]
    total: int
