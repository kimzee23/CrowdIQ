import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "testgetuser", "email": "getuser@example.com", "password": "Password123!"}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "getuser@example.com", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    me_resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_resp.json()["id"]

    # Get User Profile
    get_resp = await async_client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["username"] == "testgetuser"

@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "testupdateuser", "email": "updateuser@example.com", "password": "Password123!"}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "updateuser@example.com", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    
    # Get me
    me_resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_resp.json()["id"]

    # Update User Profile
    update_resp = await async_client.put(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"bio": "I am a new test user", "display_name": "Test Update"}
    )
    
    assert update_resp.status_code == 200
    assert update_resp.json()["bio"] == "I am a new test user"
    assert update_resp.json()["display_name"] == "Test Update"

@pytest.mark.asyncio
async def test_follow_user(async_client: AsyncClient):
    # User 1 (Follower)
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "follower_user", "email": "follower@example.com", "password": "Password123!"}
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "follower@example.com", "password": "Password123!"}
    )
    follower_token = login_resp.json()["access_token"]

    # User 2 (Target)
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "target_user", "email": "target@example.com", "password": "Password123!"}
    )
    target_login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "target@example.com", "password": "Password123!"}
    )
    target_token = target_login_resp.json()["access_token"]
    target_me_resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {target_token}"})
    target_id = target_me_resp.json()["id"]

    # Follow
    follow_resp = await async_client.post(
        f"/api/v1/users/{target_id}/follow",
        headers={"Authorization": f"Bearer {follower_token}"}
    )
    assert follow_resp.status_code == 204
    
    followers_list = await async_client.get(f"/api/v1/users/{target_id}/followers")
    assert followers_list.status_code == 200
    followers = followers_list.json()
    assert len(followers) == 1
    assert followers[0]["username"] == "follower_user"

@pytest.mark.asyncio
async def test_search_and_leaderboard(async_client: AsyncClient):
    # The users created above should appear in search and leaderboard
    search_resp = await async_client.get("/api/v1/users/search?q=test")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

    leader_resp = await async_client.get("/api/v1/users/leaderboard")
    assert leader_resp.status_code == 200
    assert isinstance(leader_resp.json(), list)
