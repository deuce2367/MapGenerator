import httpx
import asyncio

async def test_urls():
    urls = [
        ("stamen", "http://c.tile.stamen.com/watercolor/10/295/384.jpg"),
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
