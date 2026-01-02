import requests
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# 1. YOUR CREDENTIALS
TOKEN = "8133508849:AAH4d7Hr7IkrX_HBXKpJaU-JthTmldAzSjY"
CHAT_ID = "8129814833"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try:
        requests.get(url)
    except Exception as e:
        print(f"Error: {e}")

def run_automated_scan():
    watchlist = ["HAL.NS", "BEL.NS", "SBIN.NS", "RELIANCE.NS", "NTPC.NS", "INFY.NS", "TATASTEEL.NS", "ITC.NS", "HDFCBANK.NS", "BHARTIARTL.NS"]
    report = "🚀 *MORNING ENGINE REPORT*\n"
    report += "----------------------------\n"
    
    for ticker in watchlist:
        try:
            df = yf.download(ticker, period="60d", progress=False)
            curr_price = float(df['Close'].iloc[-1])
            
            # Simple Logic for Alert
            report += f"✅ *{ticker.replace('.NS', '')}*: ₹{round(curr_price, 2)}\n"
        except:
            continue
            
    report += "\n📊 [Open Your Dashboard](YOUR_STREAMLIT_URL_HERE)\n"
    report += "⚠️ *Action:* Check SL & Qty on Dashboard at 9:25 AM."
    
    send_telegram(report)

if __name__ == "__main__":
    run_automated_scan()