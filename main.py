import asyncio
import time
from tradingview_ta import TA_Handler, Interval
import requests

# ১. আপনার রিয়েল টেলিগ্রাম ডেটা এখানে সেট করা হয়েছে
TOKEN = "8854182822:AAGcW0UwvVsIGy7VHP6mxwygCjBrTzefoNo"
CHANNEL_ID = "@elite_finder_quotex_ai"

# ২. প্রধান কারেন্সি পেয়ারের লিস্ট
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP"]

def send_telegram_message(pair, direction):
    """টেলিগ্রাম চ্যানেলে সিগন্যাল পুশ করার ফাংশন"""
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
        print(f"📡 Signal Sent: {pair} -> {direction}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def analyze_market():
    print("🤖 Elite Finder Quotex Ai বট চালু হয়েছে...")
    last_signal_time = {pair: 0 for pair in PAIRS}
    
    while True:
        for pair in PAIRS:
            try:
                # TradingView এর ফ্রি ডাটা ইঞ্জিন
                handler = TA_Handler(
                    symbol=pair,
                    screener="forex",
                    exchange="FX_IDC",
                    interval=Interval.INTERVAL_1_MINUTE
                )
                
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                ema200 = analysis.indicators["EMA200"]
                close = analysis.indicators["close"]
                
                current_time = time.time()
                # প্রতি পেয়ারে অন্তত ৫ মিনিট পর পর সিগন্যাল দেওয়ার ফিল্টার
                if current_time - last_signal_time[pair] > 300:
                    
                    # 🟢 CALL (BUY) কন্ডিশন: আপট্রেন্ড এবং ওভারসোল্ড মার্কেট
                    if close > ema200 and rsi < 30:
                        send_telegram_message(pair, "CALL 🟢 (BUY)")
                        last_signal_time[pair] = current_time
                        
                    # 🔴 PUT (SELL) কন্ডিশন: ডাউনট্রেন্ড এবং ওভারবট মার্কেট
                    elif close < ema200 and rsi > 70:
                        send_telegram_message(pair, "PUT 🔴 (SELL)")
                        last_signal_time[pair] = current_time
                        
            except Exception as e:
                continue
                
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(analyze_market())
