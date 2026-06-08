# models package — import all models so Alembic autogenerate picks them up
from src.infrastructure.postgres.models.base import Base  # noqa: F401
from src.infrastructure.postgres.models.user import UserModel, FollowerModel  # noqa: F401
from src.infrastructure.postgres.models.prediction import (  # noqa: F401
    CategoryModel,
    PredictionModel,
    PredictionOptionModel,
)
from src.infrastructure.postgres.models.vote import VoteModel  # noqa: F401
from src.infrastructure.postgres.models.comment import CommentModel  # noqa: F401
from src.infrastructure.postgres.models.reputation import (  # noqa: F401
    ReputationHistoryModel,
    WalletTransactionModel,
)
from src.infrastructure.postgres.models.notification import NotificationModel  # noqa: F401
from src.infrastructure.postgres.models.ai import AIAnalysisModel  # noqa: F401

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
