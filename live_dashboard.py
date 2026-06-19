import streamlit as st
import asyncio
import websockets
import json
import pandas as pd

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
st.subheader("📈 Live Price Chart and Trading History")
graph_field=st.empty()
transaction_history_field=st.empty()

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
                last_price=trades[-1]["price"]
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
                selling_table_field.write("Theer are no pending sell orders.")
            
            if trades:
                df_trades=pd.DataFrame(trades)[["buyer","seller","price","quantity"]]
                transaction_history_field.dataframe(df_trades,use_container_width=True)

                graph_field.line_chart(df_trades["price"])
            else:
                transaction_history_field.write("No transaction history yet.")
            
                
if __name__=="__main__":
    try:
        asyncio.run(server_listener())
    except Exception as e:
        st.error(f"Could not connect to the server. Error: {e}")