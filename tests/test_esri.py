import httpx
import asyncio

async def test_urls():
    urls = [
        ("esri_hybrid_ref", "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/10/384/295"),
        ("esri_firefly", "https://server.arcgisonline.com/ArcGIS/rest/services/HalfEarth/HalfEarth_Firefly/MapServer/tile/10/384/295"),
        ("esri_dark", "https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/10/384/295"),
    ]
    async with httpx.AsyncClient() as client:
        for name, url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                print(f"{name}: {resp.status_code}")
            except Exception as e:
                print(f"{name}: {e}")

asyncio.run(test_urls())
