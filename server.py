import asyncio
from websockets.asyncio.server import serve
import json
import pandas as pd
from datetime import datetime
import os

buy_orders = []
sell_orders = []
trades = []
connected_clients=set()

async def echo(websocket):
   
    print("Server: A client has connected!")
    connected_clients.add(websocket) 
    try:
        async for message in websocket:  
            order=json.loads(message)
            if order["side"]=="buy":
                buy_orders.append(order)
                buy_orders.sort(key=lambda x: x["price"], reverse=True)
            elif order["side"]=="sell":
                sell_orders.append(order)
                sell_orders.sort(key=lambda x: x["price"])
            while(len(buy_orders)>=1 and len(sell_orders)>=1 and buy_orders[0]["price"]>=sell_orders[0]["price"]):
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if(buy_orders[0]["quantity"]==sell_orders[0]["quantity"]):
                    info={
                        "time":current_time,
                        "buyer": buy_orders[0]["user"],
                        "seller": sell_orders[0]["user"],
                        "price":sell_orders[0]["price"],
                        "quantity":sell_orders[0]["quantity"]
                    }
                    trades.append(info) 
                    buy_orders.pop(0)
                    sell_orders.pop(0)
                    
                elif(buy_orders[0]["quantity"]>sell_orders[0]["quantity"]):
                    info={
                        "time":current_time,
                        "buyer": buy_orders[0]["user"],
                        "seller": sell_orders[0]["user"],
                        "price":sell_orders[0]["price"],
                        "quantity":sell_orders[0]["quantity"]
                    }
                    trades.append(info)   
                    val=buy_orders[0]["quantity"]-sell_orders[0]["quantity"]
                    buy_orders[0]["quantity"] =val
                    sell_orders.pop(0)
                    
                elif(buy_orders[0]["quantity"]<sell_orders[0]["quantity"]):
                    info={
                        "time":current_time,
                        "buyer": buy_orders[0]["user"],
                        "seller": sell_orders[0]["user"],
                        "price":sell_orders[0]["price"],
                        "quantity":buy_orders[0]["quantity"]
                    }
                    trades.append(info)
                    val=sell_orders[0]["quantity"]-buy_orders[0]["quantity"]
                    sell_orders[0]["quantity"]=val
                    buy_orders.pop(0)
                    
                df_new_trades = pd.DataFrame([info]) 
                file_exists = os.path.exists("orders.csv") and os.path.getsize("orders.csv") > 0
                with open("orders.csv", mode='a', newline='', encoding='utf-8') as f:
                    df_new_trades.to_csv(f, index=False, header=not file_exists)
            
                
            state_packet={
                "buy_orders":buy_orders,
                "sell_orders":sell_orders,
                "trades":trades
            }
            json_state=json.dumps(state_packet)
            for client in connected_clients:
                try:
                    await client.send(json_state)
                except:
                    pass
            trades.clear()
            await websocket.send("Your order has been received!")
    finally:
        connected_clients.remove(websocket)
        print("Server: A client has been disconnected.")
async def main():
    async with serve(echo, "localhost",9000) as server:
        print("The server is up and running, listening on port 9000...")
        await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
    


