import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hybrid AI Stock Engine", layout="wide")

# Connect to Gemini AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Please add GEMINI_API_KEY to Streamlit Secrets.")

# --- 2. THE HYBRID ENGINE FUNCTIONS ---
def get_hybrid_analysis(ticker, price, trend, rsi, change):
    """The AI Layer: Interprets math into a human verdict."""
    try:
        prompt = f"""
        Analyze {ticker} for an Indian retail trader (1 Lakh capital).
        Math Data: Price ₹{price}, Trend: {trend}, RSI: {rsi:.2f}, Day Change: {change}%.
        Verdict Rules: 
        1. If RSI > 70 and Trend is Bullish, suggest 'Caution/Overbought'.
        2. If Trend is Bearish, suggest 'Avoid'.
        3. Only suggest 'Buy' if Trend is Bullish and RSI is between 40-60.
        Output: 1-sentence Verdict and 1-sentence Risk Warning.
        """
        response = ai_model.generate_content(prompt)
        return response.text
    except:
        return "AI Analysis Offline. Follow Technicals."

def calculate_hybrid_metrics(ticker):
    """The Math Layer: Calculates raw technical indicators."""
    try:
        df = yf.download(ticker, period="100d", progress=False)
        if df.empty: return None
        
        # Technical Math
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        curr_price = float(df['Close'].iloc[-1])
        ma20_val = float(df['MA20'].iloc[-1])
        rsi_val = float(df['RSI'].iloc[-1])
        day_change = ((curr_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        # Trend Logic
        trend = "BULLISH" if curr_price > ma20_val else "BEARISH"
        
        # Stop Loss Math (Using ATR for safety)
        df.ta.atr(length=14, append=True)
        atr_val = float(df['ATRr_14'].iloc[-1])
        stop_loss = curr_price - (1.8 * atr_val)
        
        return {
            "Price": round(curr_price, 2),
            "Trend": trend,
            "RSI": rsi_val,
            "Change": round(day_change, 2),
            "SL": round(stop_loss, 2)
        }
    except Exception as e:
        return None

# --- 3. UI DASHBOARD ---
st.title("🛡️ Hybrid AI Stock Engine")
st.write(f"Refined Trading Logic for {datetime.now().strftime('%d %B, %Y')}")

watchlist = ["HAL.NS", "BEL.NS", "RELIANCE.NS", "TRENT.NS", "SBIN.NS", "TATAMOTORS.NS"]

if st.button('🛡️ Start Hybrid Market Scan'):
    results = []
    for ticker in watchlist:
        m = calculate_hybrid_metrics(ticker)
        if m:
            # Pass math data to AI for final verdict
            ai_verdict = get_hybrid_analysis(ticker, m['Price'], m['Trend'], m['RSI'], m['Change'])
            
            results.append({
                "Stock": ticker.replace(".NS", ""),
                "Price": m['Price'],
                "Technical Trend": m['Trend'],
                "RSI (Strength)": round(m['RSI'], 1),
                "AI Hybrid Verdict": ai_verdict,
                "Math Stop Loss": m['SL']
            })
    
    st.table(pd.DataFrame(results))