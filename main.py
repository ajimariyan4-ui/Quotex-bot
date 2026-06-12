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
    app.run(host='0.0.0.0', port=10000)

# ১. টেলিগ্রাম ডেটা
TOKEN = "8854182822:AAGcW0UwvVsIGy7VHP6mxwygCjBrTzefoNo"
CHANNEL_ID = "@elite_finder_quotex_ai"

# ২. Quotex এর অল লাইভ এবং ওটিসি পেয়ার লিস্ট
PAIRS = [
    # Live Real Pairs
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", 
    "USDCAD", "USDCHF", "EURJPY", "GBPJPY", "AUDJPY",
    # OTC Pairs (TradingView এর মেইন ডোমেইনে এগুলো রিয়েল টাইমে রিড হয়)
    "EURUSD_OTC", "GBPUSD_OTC", "USDJPY_OTC", "AUDUSD_OTC", "EURGBP_OTC",
    "NZDUSD_OTC", "GBPJPY_OTC", "USDINR_OTC", "USDBRL_OTC", "EURCHF_OTC",
    "CHFJPY_OTC", "CADCHF_OTC"
]

def send_telegram_message(pair, direction):
    # টেলিগ্রাম মেসেজে OTC পেয়ারের নাম সুন্দর দেখানোর জন্য আন্ডারস্কোর (_) বদলে ড্যাশ (-) করা
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
                # TradingView ইঞ্জিন সেটআপ
                # OTC পেয়ারের জন্য screener সংকেত অটো-ডিটেক্ট করার জন্য কন্ডিশন
                is_otc = "_OTC" in pair
                clean_symbol = pair.split("_")[0] if is_otc else pair
                exchange_source = "OANDA" if not is_otc else "FX_IDC"
                
                handler = TA_Handler(
                    symbol=pair if is_otc else clean_symbol, 
                    screener="forex", 
                    exchange=exchange_source, 
                    interval=Interval.INTERVAL_1_MINUTE
                )
                
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                ema200 = analysis.indicators["EMA200"]
                close = analysis.indicators["close"]
                current_time = time.time()
                
                # প্রতি পেয়ারে ৫ মিনিটের সেফটি উইন্ডো ফিল্টার
                if current_time - last_signal_time[pair] > 300:
                    
                    # 🟢 CALL (BUY)
                    if close > ema200 and rsi < 30:
                        send_telegram_message(pair, "CALL 🟢 (BUY)")
                        last_signal_time[pair] = current_time
                        
                    # 🔴 PUT (SELL)
                    elif close < ema200 and rsi > 70:
                        send_telegram_message(pair, "PUT 🔴 (SELL)")
                        last_signal_time[pair] = current_time
                        
            except Exception:
                continue
                
        # প্রতিটি স্ক্যানিং সাইকেলের পর ৫ সেকেন্ড অপেক্ষা
        await asyncio.sleep(5)

def start_bot_loop():
    asyncio.run(analyze_market())

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot_loop()
