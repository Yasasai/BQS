import os
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_env_variables_loaded():
    """Regression: Ensure we are using .env and not hardcoded mid-build credentials."""
    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None, "DATABASE_URL is missing from environment"
    assert "postgres:Abcd1234" not in db_url, "Hardcoded default credentials detected in ENV!"

@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Regression: Ensure the FastAPI app boots locally."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Hitting a lightweight public endpoint or auth check
        response = await client.get("/api/auth/users")
        assert response.status_code in [200, 401], f"App failed to boot or respond. Status: {response.status_code}"
