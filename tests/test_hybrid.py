import httpx
import asyncio
import mercantile
from PIL import Image
import io

async def fetch_tile(client, url_template, x, y, z):
    url = url_template.format(z=z, x=x, y=y)
    try:
        response = await client.get(url, headers={"User-Agent": "test"}, timeout=10.0)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        return (x, y, img)
    except Exception as e:
        return (x, y, Image.new('RGBA', (256, 256), (0, 0, 0, 0)))

async def test_composite():
    urls = [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
    ]
    
    z = 10
    x, y = 384, 295
    canvas = Image.new('RGBA', (256, 256), (255, 255, 255, 255))
    
    async with httpx.AsyncClient() as client:
        for url in urls:
            _, _, img = await fetch_tile(client, url, x, y, z)
            canvas.paste(img, (0, 0), img)
            img.close()
            
    canvas.convert("RGB").save("test_hybrid.jpg")
    print("Success!")

asyncio.run(test_composite())
