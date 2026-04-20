import httpx
import asyncio

async def test_providers():
    url = "http://127.0.0.1:8001/api/generate"
    for provider in ["bing_satellite", "google_streets"]:
        payload = {
            "west": -74.0,
            "south": 40.7,
            "east": -73.9,
            "north": 40.8,
            "width": 800,
            "height": 600,
            "provider": provider,
            "constrain_aspect": True,
            "pad_color": "#000000",
            "show_scale": False,
            "show_graticule": False
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30.0)
            print(f"{provider}: len={len(resp.content)}")

asyncio.run(test_providers())
