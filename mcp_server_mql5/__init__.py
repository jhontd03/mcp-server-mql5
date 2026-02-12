"""
MQL5 MCP Server Package.

This package provides a Model Context Protocol (MCP) server that enables
AI assistants to search and retrieve documentation from the MQL5 community website.
It includes tools for searching the MQL5 documentation, extracting content,
and managing the server lifecycle.
"""

from .server import main, mcp

__all__ = ["main", "mcp"]
