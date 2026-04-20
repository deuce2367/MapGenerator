import httpx
import asyncio

async def test_wikimedia():
    url = "https://maps.wikimedia.org/osm-intl/12/2072/1409.png"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        print(f"Wikimedia with Mozilla UA: {resp.status_code}")

    headers2 = {"User-Agent": "MapGenerator/1.0"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers2)
        print(f"Wikimedia with Custom UA: {resp.status_code}")

asyncio.run(test_wikimedia())
