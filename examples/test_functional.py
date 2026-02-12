import asyncio
import sys
from typing import Any

# Force UTF-8 for Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from mcp_server_mql5.server import search_mql5_docs  # noqa: E402


async def test_real_searches() -> list[dict[str, Any]]:
    """Functional tests with real searches"""

    print("=" * 60)
    print("FUNCTIONAL TEST - MQL5 Developer Suite Server")
    print("=" * 60)

    # List of common terms in MQL5
    test_cases = [
        ("OrderSend", "Function to send orders"),
        ("MqlTradeRequest", "Trading request structure"),
        ("iMA", "Moving Average indicator"),
        ("OnTick", "Tick event function"),
        ("AccountInfoDouble", "Account info"),
        ("TerminoQueNoExiste123", "Invalid term (should fail)"),
    ]

    results = []

    for i, (search_term, description) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Searching: {search_term}")
        print(f"Description: {description}")
        print("-" * 60)

        try:
            result = await search_mql5_docs(search_term, max_chars=1000)

            # Validations
            success = True
            issues = []

            if "SOURCE:" not in result:
                issues.append("❌ Does not contain source URL")
                success = False

            if "mql5.com" not in result.lower():
                issues.append("❌ Not from mql5.com")
                success = False

            if len(result) < 50 and "No documentation found" not in result:
                issues.append("❌ Content too short")
                success = False

            if "TerminoQueNoExiste" in search_term:
                if "No documentation found" in result or "Error" in result:
                    success = True
                    issues = []
                else:
                    issues.append("❌ Should have failed but returned content")
                    success = False

            # Show result
            if success:
                print("✅ SUCCESS")
                print(f"   Length: {len(result)} chars")
                if "SOURCE:" in result:
                    url = result.split("\n")[0].replace("SOURCE:", "").strip()
                    print(f"   URL: {url}")
                print(f"   Preview: {result[:200]}...")
            else:
                print("❌ FAILED")
                for issue in issues:
                    print(f"   {issue}")

            results.append(
                {
                    "term": search_term,
                    "success": success,
                    "result_length": len(result),
                    "issues": issues,
                }
            )

            # Pause between searches to respect rate limit
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results.append(
                {
                    "term": search_term,
                    "success": False,
                    "result_length": 0,
                    "issues": [f"Exception: {str(e)}"],
                }
            )

    # Final Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"\n✅ Successful: {successful}/{total} ({successful / total * 100:.1f}%)")
    print(f"❌ Failed: {total - successful}/{total}")

    print("\nDetail:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['term']}: {r['result_length']} chars")
        if r.get("issues"):
            for issue in r["issues"]:  # type: ignore
                print(f"      {issue}")

    return results


if __name__ == "__main__":
    asyncio.run(test_real_searches())
