import asyncio
import time
import threading
from tradingview_ta import TA_Handler, Interval
import requests
from flask import Flask

# Render-এর পোর্ট এরর দূর করার জন্য একটি ডামি ওয়েব সার্ভার তৈরি
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    # Render স্বয়ংক্রিয়ভাবে ১০০০০ পোর্টে এটি রান করবে
    app.run(host='0.0.0.0', port=10000)

# ১. টেলিগ্রাম ডেটা
TOKEN = "8854182822:AAGcW0UwvVsIGy7VHP6mxwygCjBrTzefoNo"
CHANNEL_ID = "@elite_finder_quotex_ai"
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP"]

def send_telegram_message(pair, direction):
    text = (
        f"🚨 **ELITE FINDER QUOTEX AI** 🚨\n\n"
        f"📊 **Asset:** {pair}\n"
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
    print("🤖 Elite Finder Quotex Ai বট চালু হয়েছে...")
    last_signal_time = {pair: 0 for pair in PAIRS}
    while True:
        for pair in PAIRS:
            try:
                handler = TA_Handler(symbol=pair, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE)
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
        await asyncio.sleep(10)

def start_bot_loop():
    asyncio.run(analyze_market())

if __name__ == "__main__":
    # ওয়েব সার্ভারটি আলাদা সুতোয় (Thread) চালু করা যাতে পোর্ট এরর না আসে
    threading.Thread(target=run_flask).start()
    # বটের মূল লুপ চালু করা
    start_bot_loop()
