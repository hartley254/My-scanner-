# app.py - Your BTC Scanner App
import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz
import time
st.set_page_config(page_title="My Scanner", page_icon="📈", layout="centered")

st.title("📈 My Scanner v2")
st.write("BTC • ETH • SOL | London & NY Sessions")
auto_scan = st.toggle("🔄 Auto-scan every 5 min", value=True)
nairobi = pytz.timezone('Africa/Nairobi')
now = datetime.now(nairobi)
hour = now.hour

# Session
if 10 <= hour < 13:
    st.success(f"🟢 LONDON SESSION - Active | {now.strftime('%H:%M %a')}")
elif 15 <= hour < 21:
    st.success(f"🟢 NEW YORK SESSION - Active | {now.strftime('%H:%M %a')}")
else:
    st.warning(f"🟡 OFF SESSION - {now.strftime('%H:%M %a')} | Best: London 10-13, NY 15-21")

st.divider()

def check_coin(symbol):
    try:
        d4h = yf.Ticker(symbol).history(period="5d", interval="4h")
        d4h['EMA50'] = d4h['Close'].ewm(span=50, adjust=False).mean()
        trend = "BULLISH" if d4h['Close'].iloc[-1] > d4h['EMA50'].iloc[-1] else "BEARISH"

        d1h = yf.Ticker(symbol).history(period="5d", interval="1h")
        r_low = d1h['Low'].iloc[-21:-1].min()
        r_high = d1h['High'].iloc[-21:-1].max()
        sweep = False
        if trend == "BULLISH" and d1h['Low'].iloc[-1] < r_low and d1h['Close'].iloc[-1] > r_low:
            sweep = True
        if trend == "BEARISH" and d1h['High'].iloc[-1] > r_high and d1h['Close'].iloc[-1] < r_high:
            sweep = True

        d15 = yf.Ticker(symbol).history(period="1d", interval="15m")
        l_low = d15['Low'].iloc[-3:-1].min()
        l_high = d15['High'].iloc[-3:-1].max()
        bos = False
        if trend == "BULLISH" and d15['Close'].iloc[-1] > l_high:
            bos = True
        if trend == "BEARISH" and d15['Close'].iloc[-1] < l_low:
            bos = True
        
        price = d15['Close'].iloc[-1]
        return trend, sweep, bos, price
    except:
        return "ERROR", False, False, 0

if st.button("🔍 SCAN NOW", use_container_width=True):
    for coin in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        trend, sweep, bos, price = check_coin(coin)
        name = coin.replace("-USD","")
        with st.container(border=True):
            st.subheader(f"{name} - ${price:,.2f}")
            st.write(f"**Trend (4H):** {trend}")
            st.write(f"**Sweep (1H):** {'✅ YES' if sweep else '❌ NO'}")
            st.write(f"**BOS (15m):** {'✅ YES' if bos else '❌ NO'}")
            if sweep and bos:
                st.success(f"🟢 TAKE {trend} TRADE - All rules met!")
            else:
                st.error(f"🔴 NO TRADE - Stay out")

    st.info("Journal Tip: Screenshot this result and save it. After 1 week you'll see your win rate.")

st.divider()
st.caption("Rules: 4H Trend (EMA50) + 1H Sweep + 15m BOS. Only trade in London/NY sessions.")
if auto_scan:
    time.sleep(300)
    st.rerun()
