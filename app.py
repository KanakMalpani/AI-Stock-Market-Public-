import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import time
import random
import requests

# --- CONFIG ---
st.set_page_config(page_title="🛡️ AI Stock Engine", layout="wide")

# --- AI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API Key Not Found!")

# --- THE FIX: Browser Impersonation Session ---
def get_data_safely(ticker):
    session = requests.Session()
    # This header makes you look like a real Chrome browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        time.sleep(random.uniform(1, 2)) # Human-like pause
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="100d")
        return df
    except Exception:
        return None

def calculate_metrics(ticker):
    df = get_data_safely(ticker)
    if df is None or df.empty or len(df) < 20:
        return None
    
    # Logic & Math
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # ✅ FIX: .item() stops the FutureWarning
    curr_price = df['Close'].iloc[-1].item() 
    ma20_val = df['MA20'].iloc[-1].item()
    rsi_val = df['RSI'].iloc[-1].item()
    
    return {
        "Price": round(curr_price, 2),
        "Trend": "BULLISH" if curr_price > ma20_val else "BEARISH",
        "RSI": round(rsi_val, 2)
    }

# --- UI ---
st.title("🛡️ AI Stock Engine")
watchlist = ["HAL.NS", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"]

if st.button('🛡️ Scan Market'):
    results = []
    with st.spinner("Talking to Yahoo Finance..."):
        for ticker in watchlist:
            data = calculate_metrics(ticker)
            if data:
                # Simple AI prompt
                try:
                    res = ai_model.generate_content(f"Stock {ticker} is at {data['Price']}. RSI is {data['RSI']}. 1-sentence advice.")
                    verdict = res.text
                except:
                    verdict = "AI Busy."
                
                results.append({"Stock": ticker, "Price": data['Price'], "Trend": data['Trend'], "AI Advice": verdict})
    
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.error("Still Rate Limited. Yahoo has blocked this server IP. Please wait 15 mins.")