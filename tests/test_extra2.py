import httpx
import asyncio

async def test_urls():
    urls = [
        ("carto_antique", "https://cartocdn-gmaps-a.global.ssl.fastly.net/base-antique/10/295/384.png"),
        ("stadia_watercolor", "https://tiles.stadiamaps.com/tiles/stamen_watercolor/10/295/384.jpg"),
        ("stadia_terrain", "https://tiles.stadiamaps.com/tiles/stamen_terrain/10/295/384.png"),
        ("opentopomap", "https://a.tile.opentopomap.org/10/295/384.png")
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
