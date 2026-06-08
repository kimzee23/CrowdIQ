"""
CrowdIQ — OpenAI Client Wrapper
"""
from __future__ import annotations

from openai import AsyncOpenAI

from src.shared.configs.settings import settings

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Send a chat completion request and return the text response."""
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""
