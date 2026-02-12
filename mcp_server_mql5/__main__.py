"""
Entry point for the MQL5 MCP Server.

This module allows the package to be executed directly using
`python -m mcp_server_mql5`. It imports and runs the main server entry point.
"""

from .server import main

if __name__ == "__main__":
    main()
