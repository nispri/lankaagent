"""
LankaAgent MCP Server — Tourism Data Tools (FastMCP)
"""
from fastmcp import FastMCP

mcp = FastMCP("LankaAgent Tourism Data", description="Sri Lanka tourism data tools for AI agents")


@mcp.tool(name="search_attractions")
async def search_attractions(province: str | None = None, category: str | None = None, limit: int = 20) -> list[dict]:  # noqa: ARG001
    """Search Sri Lanka attractions by province and category"""
    return []


@mcp.tool(name="get_attraction_details")
async def get_attraction_details(attraction_id: str) -> dict:
    """Get full attraction details"""
    return {"id": attraction_id, "name": "Unknown", "description": "Not yet loaded"}


@mcp.tool(name="get_seasonal_pricing")
async def get_seasonal_pricing(attraction_id: str, month: int) -> dict:
    """Get peak/shoulder/low pricing for an attraction by month"""
    return {"attraction_id": attraction_id, "month": month, "season": "peak", "price_range": "TBD"}


@mcp.tool(name="get_visa_requirements")
async def get_visa_requirements(nationality: str) -> dict:
    """Get visa requirements for Sri Lanka by nationality"""
    return {"nationality": nationality, "visa_required": True, "eta_eligible": True, "fee_usd": 50}


@mcp.tool(name="get_weather_forecast")
async def get_weather_forecast(destination: str) -> dict:
    """Get 7-day weather forecast for a destination"""
    return {"destination": destination, "forecast": []}


@mcp.tool(name="get_tourism_statistics")
async def get_tourism_statistics(year: int = 2025, month: int | None = None) -> dict:
    """Get monthly tourist arrivals from SLTDA data"""
    return {"year": year, "month": month, "total_arrivals": 0, "top_markets": []}


@mcp.tool(name="get_health")
async def health() -> dict:
    """MCP server health check"""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
