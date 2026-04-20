import httpx
import asyncio

async def test_wikimedia():
    url = "https://maps.wikimedia.org/osm-intl/12/2072/1409.png"
    headers = {"User-Agent": "MapGenerator/1.0 (apsmith@example.com)"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        print(f"Wikimedia with Email UA: {resp.status_code}")

asyncio.run(test_wikimedia())
