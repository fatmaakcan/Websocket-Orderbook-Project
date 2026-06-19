import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Exchange Live Dashboard")

if "all_trades" not in st.session_state:
    st.session_state.all_trades = []


last_price_field=st.empty()

left_col,right_col=st.columns(2)
with left_col:
    st.subheader("🟢 Buy Book")
    buying_table_field=st.empty()
with right_col:
    st.subheader("🔴 Sell Book")
    selling_table_field=st.empty()

st.write("---")
st.subheader("🔢 Live NumPy Statistical Analysis")
metric_container = st.columns(4)
m1= metric_container[0].empty()
m2 = metric_container[1].empty()
m3 = metric_container[2].empty()
m4 = metric_container[3].empty()
st.write("---")
st.subheader("📈 Live Matplotlib Chart and Trading History")
graph_field = st.empty()
transaction_history_field = st.empty()

async def server_listener():
    uri="ws://localhost:9000"
    
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data=json.loads(message)
            
            if isinstance(data,str):
                continue
            
            buy_orders = data.get("buy_orders", [])
            sell_orders = data.get("sell_orders", [])
            trades = data.get("trades", [])
            
            if trades:
                st.session_state.all_trades.extend(trades)
            
            if st.session_state.all_trades:
                last_price = st.session_state.all_trades[-1]["price"]
                last_price_field.metric(label="Last Transaction Price",value=f"{last_price} $")
            else:
                last_price_field.metric(label="Last Transaction Price",value="No Transaction")
            
            if buy_orders:
                df_buy=pd.DataFrame(buy_orders)[["user","price","quantity"]]
                buying_table_field.dataframe(df_buy,use_container_width=True)
            else:
                buying_table_field.write("There are no pending buy orders.")
            
            if sell_orders:
                df_sell=pd.DataFrame(sell_orders)[["user","price","quantity"]]
                selling_table_field.dataframe(df_sell,use_container_width=True)
            else:
                selling_table_field.write("There are no pending sell orders.")
            
            if st.session_state.all_trades:
                prices =np.array([t["price"] for t in st.session_state.all_trades])
                avg=np.mean(prices)
                standart_deviation=np.std(prices)

                if avg !=0:
                    vol=standart_deviation/avg * 100
                else:
                    vol=0
                    
                last_twenty_transac=np.mean(prices[-20:])

                
                m1.metric(label="Average Price ",value=f"{avg:.2f} $")
                m2.metric(label="Standard Deviation", value=f"{standart_deviation:.2f}")
                m3.metric(label="Volatility", value=f"% {vol:.2f}")
                m4.metric(label="Last 20 Transactions Average", value=f"{last_twenty_transac:.2f} $")
                
            if st.session_state.all_trades:
                df_all_trades = pd.DataFrame(st.session_state.all_trades)
                
                if "time" in df_all_trades.columns:
                    df_all_trades["time"] = df_all_trades["time"].apply(lambda x: str(x["time"]) if isinstance(x, dict) and "time" in x else str(x))
                
                df_all_trades["Moving_Avg"] = df_all_trades["price"].rolling(window=5, min_periods=1).mean()
                
                transaction_history_field.dataframe(df_all_trades[["time", "buyer", "seller", "price", "quantity"]], use_container_width=True)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                
                ax.plot(df_all_trades["time"], df_all_trades["price"], label="Transaction Price", marker='o', linewidth=2)
                
                
                ax.plot(df_all_trades["time"], df_all_trades["Moving_Avg"], label="Moving Average", linestyle="--", linewidth=2)
                
               
                ax.set_xlabel("Time")
                ax.set_ylabel("Price $")
                ax.grid(True, linestyle=":", alpha=0.6)
                ax.legend()
                plt.xticks(rotation=45, ha='right') 
                plt.tight_layout()
                
                graph_field.pyplot(fig)
                plt.close(fig) 
            else:
                transaction_history_field.write("No transaction history yet.")
                
if __name__=="__main__":
    try:
        asyncio.run(server_listener())
    except Exception as e:
        st.error(f"Could not connect to the server. Error: {e}")