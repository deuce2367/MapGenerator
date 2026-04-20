import httpx
import asyncio

async def test_api():
    url = "http://127.0.0.1:8001/api/generate"
    
    payload1 = {
        "west": -74.0, "south": 40.7, "east": -73.9, "north": 40.8,
        "width": 800, "height": 600,
        "provider": "carto_dark",
        "constrain_aspect": True, "pad_color": "#000000",
        "show_scale": False, "show_graticule": False
    }
    payload2 = {
        **payload1,
        "provider": "google_streets"
    }
    
    async with httpx.AsyncClient() as client:
        resp1 = await client.post(url, json=payload1, timeout=30.0)
        resp2 = await client.post(url, json=payload2, timeout=30.0)
        
        with open("carto_dark.jpg", "wb") as f: f.write(resp1.content)
        with open("google_streets.jpg", "wb") as f: f.write(resp2.content)
        
        print(f"carto_dark len: {len(resp1.content)}")
        print(f"google_streets len: {len(resp2.content)}")
        print(f"Are they equal? {resp1.content == resp2.content}")

asyncio.run(test_api())
