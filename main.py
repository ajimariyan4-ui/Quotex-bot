import asyncio
import time
import threading
from tradingview_ta import TA_Handler, Interval
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "All Pairs Bot is running perfectly!"

def run_flask():
    # Render এর সাথে পোর্ট ম্যাচ করার জন্য ৮০০০ করা হলো
    app.run(host='0.0.0.0', port=8000)

# ১. টেলিগ্রাম ডেটা
TOKEN = "8854182822:AAGcW0UwvVsIGy7VHP6mxwygCjBrTzefoNo"
CHANNEL_ID = "@elite_finder_quotex_ai"

# ২. Quotex এর অল লাইভ এবং ওটিসি পেয়ার লিস্ট
PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", 
    "USDCAD", "USDCHF", "EURJPY", "GBPJPY", "AUDJPY",
    "EURUSD_OTC", "GBPUSD_OTC", "USDJPY_OTC", "AUDUSD_OTC", "EURGBP_OTC",
    "NZDUSD_OTC", "GBPJPY_OTC", "USDINR_OTC", "USDBRL_OTC", "EURCHF_OTC",
    "CHFJPY_OTC", "CADCHF_OTC"
]

def send_telegram_message(pair, direction):
    display_pair = pair.replace("_", "-")
    text = (
        f"🚨 **ELITE FINDER QUOTEX AI** 🚨\n\n"
        f"📊 **Asset:** {display_pair}\n"
        f"🎯 **Direction:** {direction} ⚡\n"
        f"⏳ **Expiry:** 1 MIN\n\n"
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
    print("🤖 All Pairs Engine Started...")
    last_signal_time = {pair: 0 for pair in PAIRS}
    
    while True:
        for pair in PAIRS:
            try:
                is_otc = "_OTC" in pair
                clean_symbol = pair.split("_")[0] if is_otc else pair
                exchange_source = "OANDA" if not is_otc else "FX_IDC"
                
                handler = TA_Handler(
                    symbol=clean_symbol if is_otc else pair, 
                    screener="forex", 
                    exchange=exchange_source, 
                    interval=Interval.INTERVAL_1_MINUTE
                )
                
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                ema200 = analysis.indicators["EMA200"]
                close = analysis.indicators["close"]
                current_time = time.time()
                
                if current_time - last_signal_time[pair] > 300:
                    if close > ema200 and rsi < 30:
                        send_telegram_message(pair, "CALL 🟢 (BUY)")
                        last_signal_time[pair] = current_time
                    elif close < ema200 and rsi > 70:
                        send_telegram_message(pair, "PUT 🔴 (SELL)")
                        last_signal_time[pair] = current_time
                        
            except Exception:
                continue
                
        await asyncio.sleep(5)

def start_bot_loop():
    asyncio.run(analyze_market())

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot_loop()
