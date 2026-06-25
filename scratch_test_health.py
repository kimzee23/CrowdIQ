import asyncio
from httpx import AsyncClient, ASGITransport
from main import app

async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        print("Status code:", response.status_code)
        print("JSON response:", response.json())
        assert response.status_code == 200
        assert response.json() == {"status": "UP"}
        print("Test passed!")

if __name__ == "__main__":
    asyncio.run(test_health())
