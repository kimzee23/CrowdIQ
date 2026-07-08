# models package — import all models so Alembic autogenerate picks them up
from src.infrastructure.persistence.models.base import Base  # noqa: F401
from src.infrastructure.persistence.models.user import UserModel, FollowerModel  # noqa: F401
from src.infrastructure.persistence.models.prediction import (  # noqa: F401
    CategoryModel,
    PredictionModel,
    PredictionOptionModel,
)
from src.infrastructure.persistence.models.vote import VoteModel  # noqa: F401
from src.infrastructure.persistence.models.comment import CommentModel  # noqa: F401
from src.infrastructure.persistence.models.reputation import (  # noqa: F401
    ReputationHistoryModel,
    WalletTransactionModel,
)
from src.infrastructure.persistence.models.notification import NotificationModel  # noqa: F401
from src.infrastructure.persistence.models.ai import AIAnalysisModel  # noqa: F401

__all__ = [
    "Base",
    "UserModel",
    "FollowerModel",
    "CategoryModel",
    "PredictionModel",
    "PredictionOptionModel",
    "VoteModel",
    "CommentModel",
    "ReputationHistoryModel",
    "WalletTransactionModel",
    "NotificationModel",
    "AIAnalysisModel",
]
