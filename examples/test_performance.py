import asyncio
import sys
import time

from mcp_server_mql5.server import search_mql5_docs

# Force UTF-8 for Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore


async def performance_test() -> None:
    """Performance and concurrency test"""

    print("=" * 60)
    print("PERFORMANCE TEST")
    print("=" * 60)

    # Test 1: Individual speed
    print("\n[TEST 1] Individual search speed")
    print("-" * 60)

    search_terms = ["OrderSend", "iMA", "OnTick"]

    for term in search_terms:
        start = time.time()
        result = await search_mql5_docs(term)
        elapsed = time.time() - start

        print(f"  {term}: {elapsed:.2f}s ({len(result)} chars)")

    # Test 2: Concurrent searches
    print("\n[TEST 2] Concurrent searches (5 simultaneous)")
    print("-" * 60)

    concurrent_terms = [
        "OrderSend",
        "iMA",
        "OnTick",
        "AccountInfoDouble",
        "PositionOpen",
    ]

    start = time.time()
    tasks = [search_mql5_docs(term) for term in concurrent_terms]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start

    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Average per search: {elapsed / len(concurrent_terms):.2f}s")
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    print(f"  Successful searches: {success_count}/{len(results)}")

    # Test 3: Cache
    print("\n[TEST 3] Cache effectiveness")
    print("-" * 60)

    term = "OrderSend"

    # First search (no cache)
    start = time.time()
    result1 = await search_mql5_docs(term)
    time1 = time.time() - start

    # Second search (cached)
    start = time.time()
    result2 = await search_mql5_docs(term)
    time2 = time.time() - start

    print(f"  First search: {time1:.2f}s")
    print(f"  Second search: {time2:.2f}s")
    print(f"  Improvement: {((time1 - time2) / time1 * 100):.1f}%")
    print(f"  Identical results: {result1 == result2}")

    # Test 4: Rate limiting
    print("\n[TEST 4] Rate limiting (15 fast searches)")
    print("-" * 60)

    start = time.time()
    for i in range(15):
        try:
            await search_mql5_docs(f"test_{i % 3}")  # Alternate terms
            print(f"  Search {i + 1}/15 completed")
        except Exception as e:
            print(f"  Search {i + 1}/15 failed: {e}")

    elapsed = time.time() - start
    print(f"\n  Total time: {elapsed:.2f}s")
    print(f"  Average: {elapsed / 15:.2f}s/search")

    # Test 5: Character limit
    print("\n[TEST 5] Respect character limit")
    print("-" * 60)

    limits = [500, 1000, 2000, 5000]

    for limit in limits:
        result = await search_mql5_docs("MqlTradeRequest", max_chars=limit)
        status = "✅" if len(result) < limit * 1.5 else "❌"
        print(f"  Limit {limit}: result {len(result)} chars ({status})")


if __name__ == "__main__":
    asyncio.run(performance_test())
