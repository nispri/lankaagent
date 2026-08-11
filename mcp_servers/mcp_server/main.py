"""
LankaAgent MCP Server entry point
"""
import sys

from mcp_server import mcp


def main() -> None:
    """Run the MCP server"""
    port = 8000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
