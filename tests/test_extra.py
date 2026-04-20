import httpx
import asyncio

async def test_urls():
    urls = [
        ("esri_delorme", "https://server.arcgisonline.com/ArcGIS/rest/services/Specialty/DeLorme_World_Base_Map/MapServer/tile/10/384/295"),
        ("osm_hot", "https://a.tile.openstreetmap.fr/hot/10/295/384.png"),
        ("cyclosm", "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/10/295/384.png")
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
