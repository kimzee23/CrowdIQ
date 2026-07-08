import pytest
from httpx import AsyncClient


# ── Helper ─────────────────────────────────────────────────────────────────────

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


# ── Tests ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient, mock_redis_store: dict):
    token = await _register_verify_login(
        async_client, "testgetuser", "getuser@example.com", mock_redis_store
    )
    me_resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    user_id = me_resp.json()["id"]

    get_resp = await async_client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["username"] == "testgetuser"


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, mock_redis_store: dict):
    token = await _register_verify_login(
        async_client, "testupdateuser", "updateuser@example.com", mock_redis_store
    )
    me_resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    user_id = me_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"bio": "I am a new test user", "display_name": "Test Update"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["bio"] == "I am a new test user"
    assert update_resp.json()["display_name"] == "Test Update"


@pytest.mark.asyncio
async def test_follow_user(async_client: AsyncClient, mock_redis_store: dict):
    follower_token = await _register_verify_login(
        async_client, "follower_user", "follower@example.com", mock_redis_store
    )
    target_token = await _register_verify_login(
        async_client, "target_user", "target@example.com", mock_redis_store
    )
    target_me_resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {target_token}"}
    )
    target_id = target_me_resp.json()["id"]

    follow_resp = await async_client.post(
        f"/api/v1/users/{target_id}/follow",
        headers={"Authorization": f"Bearer {follower_token}"},
    )
    assert follow_resp.status_code == 204

    followers_list = await async_client.get(f"/api/v1/users/{target_id}/followers")
    assert followers_list.status_code == 200
    followers = followers_list.json()
    assert len(followers) == 1
    assert followers[0]["username"] == "follower_user"


@pytest.mark.asyncio
async def test_search_and_leaderboard(async_client: AsyncClient, mock_redis_store: dict):
    search_resp = await async_client.get("/api/v1/users/search?q=test")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

    leader_resp = await async_client.get("/api/v1/users/leaderboard")
    assert leader_resp.status_code == 200
    assert isinstance(leader_resp.json(), list)
