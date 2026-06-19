import asyncio
from websockets.asyncio.client import connect
import json

async def hello():
    async with connect("ws://localhost:9000") as websocket:
        print("Client: Connected to server, sending message...")
        user=input("User: ")
        side=input("Sell or buy: ")
        price=float(input("Price: "))
        quantity=float(input("Quantity: "))

        information={
            "user":user,
            "side":side,
            "price":price,
            "quantity":quantity
        }
        json_str=json.dumps(information,ensure_ascii=False,indent=4)
        await websocket.send(json_str)
        message = await websocket.recv()
        print(f"The response from the server to the client: {message}")
    
if __name__=="__main__":
    asyncio.run(hello())