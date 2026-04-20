import httpx
import asyncio

async def test_api():
    url = "http://127.0.0.1:8001/api/generate"
    payload = {
        "west": -74.0,
        "south": 40.7,
        "east": -73.9,
        "north": 40.8,
        "width": 1920,
        "height": 1080,
        "provider": "carto_dark",
        "constrain_aspect": True,
        "pad_color": "#000000",
        "show_scale": True,
        "scale_unit": "metric",
        "show_graticule": True,
        "graticule_type": "mgrs"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=30.0)
        print(f"Status: {resp.status_code}")

asyncio.run(test_api())
