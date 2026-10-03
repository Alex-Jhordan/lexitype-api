import os
import pytest
import httpx

os.environ["GROQ_API_KEY"] = "dummy-key"

from app.main import app

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client