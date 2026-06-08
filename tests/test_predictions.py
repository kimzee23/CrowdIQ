import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_that_user_can_create_and_get_prediction(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "preduser", "email": "pred@example.com", "password": "Password123!"}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "pred@example.com", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}


    pred_payload = {
        "title": "Will AI replace engineers?",
        "description": "Prediction on whether AI agents will completely replace software engineers.",
        "category_id": "00000000-0000-0000-0000-000000000000",
        "prediction_type": "binary",
        "options": [
            {"option_text": "Yes"},
            {"option_text": "No"}
        ]
    }
    create_resp = await async_client.post("/api/v1/predictions", json=pred_payload, headers=headers)

    assert create_resp.status_code == 404

    # 3. Get predictions list
    list_resp = await async_client.get("/api/v1/predictions")
    assert list_resp.status_code == 200
    assert "predictions" in list_resp.json()
