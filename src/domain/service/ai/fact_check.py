"""
CrowdIQ — Fact Check Use Case (AI)
"""
from __future__ import annotations

import json

from src.application.dto.ai import AIResponse, FactCheckRequest
from src.infrastructure.ai.client import chat_completion

_SYSTEM = (
    "You are CrowdIQ, an AI prediction intelligence assistant. "
    "Be concise, analytical, and return structured JSON when asked."
)


class FactCheck:
    async def execute(self, req: FactCheckRequest) -> AIResponse:
        prompt = (
            f"Fact-check this claim:\n'{req.claim}'\n\n"
            f'Respond as JSON: {{"result": "true|false|unverifiable", "confidence": 0.0-1.0, "summary": "..."}}'
        )
        raw = await chat_completion(_SYSTEM, prompt)
        try:
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
