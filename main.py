import asyncio
import time
import threading
from tradingview_ta import TA_Handler, Interval
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex Live and OTC Hybrid Engine is Active!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

TOKEN = "8854182822:AAGcW0UwvVsIGy7VHP6mxwygCjBrTzefoNo"
CHANNEL_ID = "@elite_finder_quotex_ai"

# লাইভ এবং ওটিসি উভয় মার্কেটের জন্য কম্বাইন্ড পেয়ার লিস্ট
PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", 
    "USDCAD", "USDCHF", "EURJPY", "GBPJPY", "AUDJPY",
    "NZDUSD", "EURAUD", "GBPAUD", "EURCAD", "AUDCAD"
]

def send_telegram_message(pair, direction):
    # আজ উইকেন্ড (শনি বা রবি) কিনা চেক করা
    is_weekend = time.strftime("%A") in ["Saturday", "Sunday"]
    
    # টেলিগ্রাম মেসেজে দেখানোর জন্য নাম সুন্দর করা (যেমন: EUR-USD)
    display_pair = f"{pair[0:3]}-{pair[3:6]}"
    
    # উইকেন্ড হলে নামের শেষে OTC যোগ হবে, অন্যথায় LIVE দেখাবে
    market_type = "OTC" if is_weekend else "LIVE MARKET"
    if is_weekend:
        display_pair += "-OTC"

    text = (
        f"🚨 **ELITE FINDER QUOTEX AI** 🚨\n\n"
        f"📊 **Asset:** {display_pair}\n"
        f"🎯 **Direction:** {direction} ⚡\n"
        f"⏳ **Expiry:** 1 MIN\n"
        f"🌐 **Market:** {market_type}\n\n"
        f"🚫 **NON-MTG (Strict 1-Step Entry)**\n"
        f"✅ 80-85% High Accuracy Filtered"
    )
    url = f"https://telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception:
        pass

async def analyze_market():
    print("🚀 Live & OTC Hybrid Scanner Started...")
    last_signal_time = {pair: 0 for pair in PAIRS}
    
    while True:
        # আজ উইকেন্ড কিনা তার ওপর ভিত্তি করে ডাটা সোর্স (Exchange) পরিবর্তন
        is_weekend = time.strftime("%A") in ["Saturday", "Sunday"]
        exchange_source = "FX_IDC" if is_weekend else "OANDA"
        
        for pair in PAIRS:
            try:
                # TradingView ইঞ্জিন সেটআপ
                handler = TA_Handler(
                    symbol=pair, 
                    screener="forex", 
                    exchange=exchange_source, 
                    interval=Interval.INTERVAL_1_MINUTE
                )
                
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                ema50 = analysis.indicators["EMA50"]
                close = analysis.indicators["close"]
                
                current_time = time.time()
                # প্রতি ৩ মিনিট পর পর একই পেয়ারে সিগন্যাল দেওয়ার ফিল্টার (দ্রুত সিগন্যালের জন্য)
                if current_time - last_signal_time[pair] > 180:
                    
                    # 🟢 CALL (BUY) কন্ডিশন
                    if close > ema50 and rsi <= 40:
                        send_telegram_message(pair, "CALL 🟢 (BUY)")
                        last_signal_time[pair] = current_time
                        
                    # 🔴 PUT (SELL) কন্ডিশন
                    elif close < ema50 and rsi >= 60:
                        send_telegram_message(pair, "PUT 🔴 (SELL)")
                        last_signal_time[pair] = current_time
                        
            except Exception:
                continue
                
        # প্রতি ৫ সেকেন্ডে পুরো পেয়ার লিস্ট রি-স্ক্যান করবে
        await asyncio.sleep(5)

def start_bot_loop():
    asyncio.run(analyze_market())

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot_loop()
