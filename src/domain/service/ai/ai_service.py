"""
CrowdIQ — AI Service
Wraps OpenAI calls for prediction analysis, fact-checking, sentiment, etc.
"""
from __future__ import annotations

import json

from src.application.dto.ai import (
    AIResponse,
    AnalyzeRequest,
    FactCheckRequest,
    ProbabilityRequest,
    SentimentRequest,
    TrendAnalysisRequest,
)
from src.infrastructure.ai.client import chat_completion


_SYSTEM = (
    "You are CrowdIQ, an AI prediction intelligence assistant. "
    "Be concise, analytical, and return structured JSON when asked."
)


class AIService:
    async def analyze(self, req: AnalyzeRequest) -> AIResponse:
        prompt = (
            f"Analyze this prediction claim for credibility, evidence, and likely outcome:\n"
            f"Prediction ID: {req.prediction_id}\n"
            f"Text: {req.text}\n\n"
            f'Respond as JSON: {{"summary": "...", "confidence": 0.0-1.0, "sentiment": "positive|negative|neutral"}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        return self._parse_response(raw)

    async def fact_check(self, req: FactCheckRequest) -> AIResponse:
        prompt = (
            f"Fact-check this claim:\n'{req.claim}'\n\n"
            f'Respond as JSON: {{"result": "true|false|unverifiable", "confidence": 0.0-1.0, "summary": "..."}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        return self._parse_response(raw)

    async def estimate_probability(self, req: ProbabilityRequest) -> AIResponse:
        prompt = (
            f"Estimate the probability (0-100%) for prediction {req.prediction_id}.\n"
            f"Context: {req.context or 'No additional context'}\n\n"
            f'Respond as JSON: {{"probability": 0-100, "confidence": 0.0-1.0, "reasoning": "..."}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        return self._parse_response(raw)

    async def analyze_sentiment(self, req: SentimentRequest) -> AIResponse:
        prompt = (
            f"Analyze the sentiment of the following text:\n'{req.text}'\n\n"
            f'Respond as JSON: {{"sentiment": "positive|negative|neutral", "score": -1.0 to 1.0}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        return self._parse_response(raw)

    async def analyze_trend(self, req: TrendAnalysisRequest) -> AIResponse:
        prompt = (
            f"Analyze current trends for the topic: '{req.topic}'.\n"
            f'Respond as JSON: {{"summary": "...", "direction": "rising|falling|stable", "confidence": 0.0-1.0}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        return self._parse_response(raw)

    @staticmethod
    def _parse_response(raw: str) -> AIResponse:
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(cleaned)
            return AIResponse(
                result=data.get("summary") or data.get("result") or raw,
                confidence=data.get("confidence"),
                sentiment=data.get("sentiment"),
                metadata=data,
            )
        except (json.JSONDecodeError, KeyError):
            return AIResponse(result=raw)
