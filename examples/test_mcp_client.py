import asyncio
import sys

# Force UTF-8 for Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402


async def test_with_mcp_client() -> None:
    """Test using official MCP client"""

    print("Starting MCP server...")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server_mql5.server"],  # Adjust name
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            print("✅ Server connected")
            print("\n" + "=" * 60)

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                desc = tool.description[:100] if tool.description else ""
                print(f"  - {tool.name}: {desc}...")

            print("\n" + "=" * 60)
            print("EXECUTING SEARCHES")
            print("=" * 60)

            # Test cases
            searches = ["OrderSend", "iMA", "OnTick", "MqlTradeRequest"]

            for search_term in searches:
                print(f"\n🔍 Searching: {search_term}")
                print("-" * 40)

                try:
                    # Call the tool
                    result = await session.call_tool(
                        "search_mql5_docs", arguments={"search_term": search_term}
                    )

                    # Process result
                    if result.content:
                        content_item = result.content[0]
                        # Check type via hasattr (safe duck-typing)
                        # Workaround for mypy union inference issues
                        if hasattr(content_item, "text"):
                            content = getattr(content_item, "text")
                        else:
                            content = "Non-text content"
                    else:
                        content = "No content"

                    print("✅ Result received")
                    print(f"   Length: {len(content)} chars")

                    if "SOURCE:" in content:
                        lines = content.split("\n")
                        print(f"   {lines[0]}")

                    print(f"   Preview: {content[:150]}...")

                except Exception as e:
                    print(f"❌ Error: {str(e)}")

                await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(test_with_mcp_client())
