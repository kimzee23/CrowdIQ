# models package — import all models so Alembic autogenerate picks them up
from src.infrastructure.persistence.entity.base import Base  # noqa: F401
from src.infrastructure.persistence.entity.user import UserModel, FollowerModel  # noqa: F401
from src.infrastructure.persistence.entity.prediction import (  # noqa: F401
    CategoryModel,
    PredictionModel,
    PredictionOptionModel,
)
from src.infrastructure.persistence.entity.vote import VoteModel  # noqa: F401
from src.infrastructure.persistence.entity.comment import CommentModel  # noqa: F401
from src.infrastructure.persistence.entity.reputation import (  # noqa: F401
    ReputationHistoryModel,
    WalletTransactionModel,
)
from src.infrastructure.persistence.entity.notification import NotificationModel  # noqa: F401
from src.infrastructure.persistence.entity.ai import AIAnalysisModel  # noqa: F401

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
