"""
CrowdIQ — AI Service Package
"""
from __future__ import annotations

from src.domain.service.ai.analyze_prediction import AnalyzePrediction
from src.domain.service.ai.fact_check import FactCheck

__all__ = ["AnalyzePrediction", "FactCheck"]

from .ai_service import AIService
__all__.append('AIService')
