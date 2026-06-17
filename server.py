import asyncio
from websockets.asyncio.server import serve

async def echo(websocket):
    print("sunucu: bir client bağlandı!")
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost",9000) as server:
        print("sunucu ayağa kalktı, port 9000 dinleniyor...")
        await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
    
