import httpx
import asyncio
import json

async def f():
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://127.0.0.1:8001/api/providers')
        print(json.dumps(resp.json(), indent=2))

asyncio.run(f())
