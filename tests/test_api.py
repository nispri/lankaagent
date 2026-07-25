"""LankaAgent test suite"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client() -> AsyncClient:
    """Test client fixture"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root endpoint returns correct response"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "LankaAgent API"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient) -> None:
    """Test health liveness endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_readiness(client: AsyncClient) -> None:
    """Test health readiness endpoint"""
    response = await client.get("/health/ready")
    assert response.status_code == 503  # No DB/Redis running in test
    data = response.json()
    assert data["status"] == "not_ready"


@pytest.mark.asyncio
async def test_api_docs_available(client: AsyncClient) -> None:
    """Test OpenAPI docs are accessible"""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient) -> None:
    """Test CORS headers are present"""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_404_handler(client: AsyncClient) -> None:
    """Test 404 handling"""
    response = await client.get("/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_correlation_id(client: AsyncClient) -> None:
    """Test correlation ID is returned"""
    response = await client.get("/health", headers={"X-Correlation-ID": "test-correlation-id"})
    assert response.headers.get("X-Correlation-ID") == "test-correlation-id"


@pytest.mark.asyncio
async def test_leads_endpoint(client: AsyncClient) -> None:
    """Test leads endpoint returns list"""
    response = await client.get("/api/v1/leads")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_auth_login(client: AsyncClient) -> None:
    """Test auth login endpoint"""
    response = await client.post("/api/v1/auth/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_spec(client: AsyncClient) -> None:
    """Test OpenAPI spec is valid"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "paths" in spec
    assert "/health" in spec["paths"]