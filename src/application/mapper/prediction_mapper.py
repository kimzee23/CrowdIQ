"""
CrowdIQ — Prediction Mapper
"""
from src.application.dto.prediction import PredictionResponse, PredictionOptionResponse
from src.application.dto.vote import VoteResponse
from src.application.dto.comment import CommentResponse
from src.domain.model.prediction import Prediction
from src.domain.model.vote import Vote
from src.domain.model.comment import Comment


def to_option_response(o) -> PredictionOptionResponse:
    return PredictionOptionResponse(
        id=o.id,
        prediction_id=o.prediction_id,
        option_text=o.option_text,
        vote_count=o.vote_count,
    )


def to_prediction_response(p: Prediction) -> PredictionResponse:
    return PredictionResponse(
        id=p.id,
        creator_id=p.creator_id,
        title=p.title,
        description=p.description,
        category_id=p.category_id,
        prediction_type=p.prediction_type.value,
        status=p.status.value,
        options=[to_option_response(o) for o in p.options],
        close_at=p.close_at,
        resolved_at=p.resolved_at,
        resolved_option_id=p.resolved_option_id,
        view_count=p.view_count,
        total_votes=p.total_votes(),
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def to_vote_response(v: Vote) -> VoteResponse:
    return VoteResponse(
        id=v.id,
        user_id=v.user_id,
        prediction_id=v.prediction_id,
        option_id=v.option_id,
        confidence=v.confidence,
        stake=v.stake,
        created_at=v.created_at,
    )


def to_comment_response(c: Comment) -> CommentResponse:
    return CommentResponse(
        id=c.id,
        prediction_id=c.prediction_id,
        user_id=c.user_id,
        content=c.content,
        parent_id=c.parent_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )
