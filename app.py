import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai

# --- CONFIG ---
st.set_page_config(page_title="AI Stock Engine", layout="wide")

# --- DEBUGGING SECRETS ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API Key Not Found! Go to Settings > Secrets and add GEMINI_API_KEY")

def calculate_metrics(ticker):
    try:
        # We fetch 100 days to ensure we have enough data for the Moving Average
        df = yf.download(ticker, period="100d", progress=False)
        
        if df.empty or len(df) < 20:
            return None
        
        # Technical Logic
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        curr_price = float(df['Close'].iloc[-1])
        ma20_val = float(df['MA20'].iloc[-1])
        rsi_val = float(df['RSI'].iloc[-1])
        
        # Trend and Safety
        trend = "BULLISH" if curr_price > ma20_val else "BEARISH"
        
        return {
            "Price": round(curr_price, 2),
            "Trend": trend,
            "RSI": round(rsi_val, 2)
        }
    except Exception as e:
        st.warning(f"Could not get data for {ticker}: {e}")
        return None

st.title("🛡️ AI Stock Engine (Debug Mode)")

# Simple list to test
watchlist = ["HAL.NS", "RELIANCE.NS", "SBIN.NS"]

if st.button('🛡️ Run Market Scan'):
    results = []
    with st.spinner("Analyzing Market Data..."):
        for ticker in watchlist:
            data = calculate_metrics(ticker)
            if data:
                # Try AI Analysis
                try:
                    prompt = f"Stock: {ticker}, Price: {data['Price']}, RSI: {data['RSI']}. Give a 1-sentence trading advice for a retail investor."
                    response = ai_model.generate_content(prompt)
                    verdict = response.text
                except:
                    verdict = "AI Busy. Check Technicals."
                
                results.append({
                    "Stock": ticker,
                    "Price": data['Price'],
                    "RSI": data['RSI'],
                    "Trend": data['Trend'],
                    "AI Advice": verdict
                })
        
    if results:
        st.table(pd.DataFrame(results))
    else:
        st.error("No data found. Check your internet or Ticker symbols.")