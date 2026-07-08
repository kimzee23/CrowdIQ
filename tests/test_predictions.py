import pytest
from httpx import AsyncClient


async def _register_verify_login(
    async_client: AsyncClient,
    username: str,
    email: str,
    mock_redis_store: dict,
) -> str:
    """Register → verify OTP → login → return access_token."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": "Password123!"},
    )
    otp = mock_redis_store[f"otp:{email}"]
    await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": email, "otp": otp}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    return login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_that_user_can_create_and_get_prediction(
    async_client: AsyncClient, mock_redis_store: dict
):
    token = await _register_verify_login(
        async_client, "preduser", "pred@example.com", mock_redis_store
    )
    headers = {"Authorization": f"Bearer {token}"}

    pred_payload = {
        "title": "Will AI replace engineers?",
        "description": "Prediction on whether AI agents will completely replace software engineers.",
        "category_id": "00000000-0000-0000-0000-000000000000",
        "prediction_type": "binary",
        "options": [{"option_text": "Yes"}, {"option_text": "No"}],
    }
    create_resp = await async_client.post(
        "/api/v1/predictions", json=pred_payload, headers=headers
    )
    assert create_resp.status_code == 404

    list_resp = await async_client.get("/api/v1/predictions")
    assert list_resp.status_code == 200
    assert "predictions" in list_resp.json()
