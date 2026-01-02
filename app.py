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

# --- CACHED DATA FETCHING (Prevents Rate Limits) ---
@st.cache_data(ttl=300) # Saves data for 5 minutes
def get_stock_data(ticker):
    """Downloads data and handles the Yahoo traffic jam logic."""
    try:
        # Random delay to mimic a human user
        time.sleep(random.uniform(1.0, 2.0)) 
        df = yf.download(ticker, period="100d", progress=False)
        return df
    except Exception as e:
        return None

def calculate_metrics(ticker):
    df = get_stock_data(ticker)
    
    if df is None or df.empty or len(df) < 20:
        return None
    
    try:
        # Technical Math
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # ✅ THE FIX: Using .item() to extract single values safely
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
st.markdown("### Scanning for ₹1 Lakh Portfolio Safety")

watchlist = ["HAL.NS", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"]

if st.button('🛡️ Start Market Scan'):
    results = []
    with st.spinner("Analyzing Technicals & Asking Gemini AI..."):
        for ticker in watchlist:
            data = calculate_metrics(ticker)
            if data:
                # Ask AI for advice
                try:
                    prompt = f"Stock: {ticker}, Price: {data['Price']}, RSI: {data['RSI']}, Trend: {data['Trend']}. Give a 1-sentence trading advice."
                    response = ai_model.generate_content(prompt)
                    verdict = response.text
                except:
                    verdict = "AI is busy. Technical Trend: " + data['Trend']
                
                results.append({
                    "Stock": ticker,
                    "Price": data['Price'],
                    "RSI": data['RSI'],
                    "Trend": data['Trend'],
                    "AI Analysis": verdict
                })
        
    if results:
        # Professional Table View
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("🚨 Yahoo Finance is currently blocking requests from the cloud. Please wait 10-15 minutes and click again.")

st.divider()
st.info("Tip: If the table is empty, Yahoo is rate-limiting the shared Streamlit server. Caching is now enabled to reduce this risk.")