import httpx
import asyncio

async def test_urls():
    urls = [
        ("hikebike", "https://tiles.wmflabs.org/hikebike/10/295/384.png"),
        ("toner", "https://stamen-tiles.a.ssl.fastly.net/toner/10/295/384.png"),
        ("osm_fr", "https://a.tile.openstreetmap.fr/osmfr/10/295/384.png")
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
