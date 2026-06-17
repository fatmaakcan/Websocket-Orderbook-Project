import asyncio
from websockets.asyncio.client import connect

async def hello():
    async with connect("ws://localhost:9000") as websocket:
        print("Client: Sunucuya bağlanıldı, mesaj gönderiliyor...")
        await websocket.send("Hello world!")
        message = await websocket.recv()
        print(f"Client'a sunucudan gelen cevap: {message}")
    
if __name__=="__main__":
    asyncio.run(hello())