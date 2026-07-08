"""
CrowdIQ — Wallet Service Package
"""
from __future__ import annotations

from src.domain.service.wallet.award_points import AwardPoints
from src.domain.service.wallet.deduct_points import DeductPoints

__all__ = ["AwardPoints", "DeductPoints"]

from .wallet_service import WalletService
__all__.append('WalletService')
