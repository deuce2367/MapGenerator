import httpx
import asyncio

async def test_urls():
    urls = [
        ("tf_outdoors", "https://tile.thunderforest.com/outdoors/10/295/384.png"),
        ("tf_landscape", "https://tile.thunderforest.com/landscape/10/295/384.png")
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
