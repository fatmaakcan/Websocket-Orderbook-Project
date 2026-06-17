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
            buy_orders.sort(key=lambda x: x["price"], reverse=True)
        elif order["side"]=="sell":
            sell_orders.append(order)
            sell_orders.sort(key=lambda x: x["price"])
        while(len(buy_orders)>=1 and len(sell_orders)>=1 and buy_orders[0]["price"]>=sell_orders[0]["price"]):
            if(buy_orders[0]["quantity"]==sell_orders[0]["quantity"]):
                info={
                    "price":sell_orders[0]["price"],
                    "quantity":sell_orders[0]["quantity"]
                }
                trades.append(info) 
                buy_orders.pop(0)
                sell_orders.pop(0)
            elif(buy_orders[0]["quantity"]>sell_orders[0]["quantity"]):
                info={
                    "price":sell_orders[0]["price"],
                    "quantity":sell_orders[0]["quantity"]
                }
                trades.append(info)   
                val=buy_orders[0]["quantity"]-sell_orders[0]["quantity"]
                buy_orders[0]["quantity"] =val
                sell_orders.pop(0)
            elif(buy_orders[0]["quantity"]<sell_orders[0]["quantity"]):
                info={
                    "price":sell_orders[0]["price"],
                    "quantity":sell_orders[0]["quantity"]
                }
                trades.append(info)
                val=sell_orders[0]["quantity"]-buy_orders[0]["quantity"]
                sell_orders[0]["quantity"]=val
                buy_orders.pop(0)
            
        await websocket.send("Emriniz alındı!")
async def main():
    async with serve(echo, "localhost",9000) as server:
        print("sunucu ayağa kalktı, port 9000 dinleniyor...")
        await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
    


