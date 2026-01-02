import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="🛡️ AI Stock Engine", layout="wide")

# --- AI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API Key Not Found! Go to Settings > Secrets and add GEMINI_API_KEY")

# --- THE ENGINE FUNCTION ---
def calculate_metrics(ticker):
    try:
        # 1. Anti-Blocking Pause
        time.sleep(random.uniform(1.0, 2.5)) 
        
        # 2. Download Data
        df = yf.download(ticker, period="100d", progress=False)
        
        if df.empty or len(df) < 20:
            return None
        
        # 3. Technical Math
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # 4. Extract single values safely (Fixes the FutureWarning)
        curr_price = df['Close'].iloc[-1].item() 
        ma20_val = df['MA20'].iloc[-1].item()
        rsi_val = df['RSI'].iloc[-1].item()
        
        trend = "BULLISH" if curr_price > ma20_val else "BEARISH"
        
        return {
            "Price": round(curr_price, 2),
            "Trend": trend,
            "RSI": round(rsi_val, 2)
        }
    except Exception as e:
        if "Rate limited" in str(e):
            st.error(f"🚨 Yahoo is blocking this request. Try again in 15 mins. ({ticker})")
        return None

# --- UI INTERFACE ---
st.title("🛡️ AI Stock Engine")
st.write("Using Technical Analysis + Gemini AI to analyze your portfolio.")

watchlist = ["HAL.NS", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"]

if st.button('🛡️ Start Market Scan'):
    results = []
    with st.spinner("Talking to Markets & AI..."):
        for ticker in watchlist:
            data = calculate_metrics(ticker)
            if data:
                # Ask AI for advice
                try:
                    prompt = f"Stock: {ticker}, Price: {data['Price']}, RSI: {data['RSI']}, Trend: {data['Trend']}. Give a 1-sentence trading advice."
                    response = ai_model.generate_content(prompt)
                    verdict = response.text
                except:
                    verdict = "AI is thinking. Refer to Technicals."
                
                results.append({
                    "Stock": ticker,
                    "Price": data['Price'],
                    "RSI": data['RSI'],
                    "Trend": data['Trend'],
                    "AI Analysis": verdict
                })
        
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("The table is empty. This usually means Yahoo Finance is temporarily rate-limiting the connection. Please wait a few minutes and try again.")