"""
CrowdIQ — Search Service Package
"""
from __future__ import annotations

from src.domain.service.search.search_predictions import SearchPredictions

__all__ = ["SearchPredictions"]

from .search_service import SearchService
__all__.append('SearchService')
