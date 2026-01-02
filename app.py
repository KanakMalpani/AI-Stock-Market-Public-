import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="🛡️ Hybrid AI Stock Engine", layout="wide")

# --- AI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API Key Not Found! Go to Settings > Secrets and add GEMINI_API_KEY")

# --- DATA FETCHING (Rate Limit Workaround) ---
@st.cache_data(ttl=600)  # Caches data for 10 mins to avoid hitting Yahoo too often
def get_stock_data(ticker):
    try:
        # Add a random delay to look like a human visitor
        time.sleep(random.uniform(1.0, 3.0))
        
        # We download data while specifying a "User-Agent" to bypass blocks
        df = yf.download(ticker, period="100d", progress=False, timeout=10)
        return df
    except Exception:
        return None

def calculate_metrics(ticker):
    df = get_stock_data(ticker)
    
    if df is None or df.empty or len(df) < 20:
        return None
    
    try:
        # Technical Math
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # ✅ THE FIX: Using .item() to extract values safely (Stops the FutureWarning)
        curr_price = df['Close'].iloc[-1].item() 
        ma20_val = df['MA20'].iloc[-1].item()
        rsi_val = df['RSI'].iloc[-1].item()
        
        trend = "BULLISH" if curr_price > ma20_val else "BEARISH"
        
        return {
            "Price": round(curr_price, 2),
            "Trend": trend,
            "RSI": round(rsi_val, 2)
        }
    except Exception:
        return None

# --- UI INTERFACE ---
st.title("🛡️ Hybrid AI Stock Engine")
st.write("Real-time Analysis for your ₹1 Lakh Portfolio")

watchlist = ["HAL.NS", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"]

if st.button('🛡️ Start Market Scan'):
    results = []
    with st.spinner("Bypassing firewalls and analyzing data..."):
        for ticker in watchlist:
            data = calculate_metrics(ticker)
            if data:
                try:
                    prompt = f"Stock: {ticker}, Price: {data['Price']}, RSI: {data['RSI']}, Trend: {data['Trend']}. 1-sentence trading advice for India market."
                    response = ai_model.generate_content(prompt)
                    verdict = response.text
                except:
                    verdict = f"AI is busy. Technical trend is {data['Trend']}."
                
                results.append({
                    "Stock": ticker,
                    "Price": data['Price'],
                    "RSI": data['RSI'],
                    "Trend": data['Trend'],
                    "AI Advice": verdict
                })
        
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.warning("⚠️ Yahoo is still blocking the connection. Because Streamlit Cloud uses shared IPs, this happens often. Please wait 15 minutes and click again.")