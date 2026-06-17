import asyncio
from websockets.asyncio.server import serve
import json

buy_orders = []
sell_orders = []
trades = []

async def echo(websocket):
    print("sunucu: bir client bağlandı!")
    async for message in websocket:  
        order=json.loads(message)
        if order["side"]=="buy":
            buy_orders.append(order)
        elif order["side"]=="sell":
            sell_orders.append(order)
        await websocket.send("Emriniz alındı!")
async def main():
    async with serve(echo, "localhost",9000) as server:
        print("sunucu ayağa kalktı, port 9000 dinleniyor...")
        await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
    
