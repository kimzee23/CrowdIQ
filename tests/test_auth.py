import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_that_user_can_register(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "ade_ope",
            "email": "ade@gmail.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_that_user_can_login(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "Adelogin",
            "email": "Adelogin@gmail.com",
            "password": "Password123!"
        }
    )
    
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "Adelogin@gmail.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_that_get_profile(async_client: AsyncClient):
    # Register and login
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "Password123!"
        }
    )
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "Password123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get Me
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"
