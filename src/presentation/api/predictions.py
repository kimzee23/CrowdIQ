"""
CrowdIQ — Predictions Router  /api/v1/predictions
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, status

from src.application.dto.prediction import (
    CreatePredictionRequest,
    PredictionListResponse,
    PredictionOptionResponse,
    PredictionResponse,
    ResolvePredictionRequest,
    UpdatePredictionRequest,
)
from src.application.dto.vote import CastVoteRequest, VoteListResponse, VoteResponse
from src.application.dto.comment import CommentListResponse, CommentResponse
from src.domain.service.comment import CommentService
from src.domain.service.prediction import PredictionService
from src.domain.service.vote import VoteService
from src.domain.model.prediction import Prediction
from src.domain.model.user import User
from src.domain.model.vote import Vote
from src.domain.model.comment import Comment
from src.presentation.api.deps import (
    get_comment_service,
    get_current_user,
    get_prediction_service,
    get_vote_service,
)
from src.infrastructure.config.utils.helpers import paginate
from src.application.mapper.prediction_mapper import to_prediction_response, to_vote_response, to_comment_response

router = APIRouter(prefix="/predictions", tags=["Predictions"])





# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    req: CreatePredictionRequest,
    current_user: User = Depends(get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
):
    return to_prediction_response(await svc.create(req, current_user))


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    category_id: Optional[str] = None,
    svc: PredictionService = Depends(get_prediction_service),
):
    sk, lm = paginate(skip, limit)
    preds = await svc.list_all(sk, lm, status, category_id)
    return PredictionListResponse(
        predictions=[to_prediction_response(p) for p in preds],
        total=len(preds), skip=sk, limit=lm,
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    svc: PredictionService = Depends(get_prediction_service),
):
    return to_prediction_response(await svc.get(prediction_id))


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: str,
    req: UpdatePredictionRequest,
    current_user: User = Depends(get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
):
    return to_prediction_response(await svc.update(prediction_id, req, current_user))


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
):
    await svc.delete(prediction_id, current_user)


@router.post("/{prediction_id}/close", response_model=PredictionResponse)
async def close_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
):
    return to_prediction_response(await svc.close(prediction_id, current_user))


@router.post("/{prediction_id}/resolve", response_model=PredictionResponse)
async def resolve_prediction(
    prediction_id: str,
    req: ResolvePredictionRequest,
    current_user: User = Depends(get_current_user),
    svc: PredictionService = Depends(get_prediction_service),
):
    return to_prediction_response(await svc.resolve(prediction_id, req, current_user))


# ── Votes ─────────────────────────────────────────────────────────────────────

@router.post("/{prediction_id}/vote", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    prediction_id: str,
    req: CastVoteRequest,
    current_user: User = Depends(get_current_user),
    vote_svc: VoteService = Depends(get_vote_service),
):
    return to_vote_response(await vote_svc.cast_vote(prediction_id, req, current_user))


@router.get("/{prediction_id}/votes", response_model=VoteListResponse)
async def get_votes(
    prediction_id: str,
    skip: int = 0,
    limit: int = 50,
    vote_svc: VoteService = Depends(get_vote_service),
):
    sk, lm = paginate(skip, limit)
    votes = await vote_svc.get_votes_for_prediction(prediction_id, sk, lm)
    return VoteListResponse(votes=[to_vote_response(v) for v in votes], total=len(votes))


@router.post("/{prediction_id}/stake", response_model=VoteResponse)
async def stake(
    prediction_id: str,
    req,
    current_user: User = Depends(get_current_user),
    vote_svc: VoteService = Depends(get_vote_service),
):
    return to_vote_response(await vote_svc.stake_points(prediction_id, req, current_user))


# ── Comments ─────────────────────────────────────────────────────────────────

@router.get("/{prediction_id}/comments", response_model=CommentListResponse)
async def get_comments(
    prediction_id: str,
    skip: int = 0,
    limit: int = 50,
    comment_svc: CommentService = Depends(get_comment_service),
):
    sk, lm = paginate(skip, limit)
    comments = await comment_svc.get_comments(prediction_id, sk, lm)
    return CommentListResponse(comments=[to_comment_response(c) for c in comments], total=len(comments))
