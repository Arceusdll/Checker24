from flask import Flask, request
import os
import time
import threading
from playwright.sync_api import sync_playwright
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID") or "YOUR_CHAT_ID"
PRODUCT_URL = os.environ.get("PRODUCT_URL") or "https://shop.amul.com/en/product/amul-dark-chocolate-150g"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is running"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram error:", e)

def check_stock():
    while True:
        try:
            print("🕵️‍♂️ Checking stock status...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(PRODUCT_URL, timeout=60000)
                page.wait_for_timeout(3000)
                if page.query_selector("button.btn.btn-primary:has-text('Add to Cart')"):
                    print("✅ IN STOCK!")
                    send_telegram_message(f"🚨 *Product is IN STOCK!* 🛒\n[Buy Now]({PRODUCT_URL})")
                else:
                    print("❌ Still out of stock.")
                browser.close()
        except Exception as e:
            print("⚠️ Error:", e)
        time.sleep(10)

# Run checker in background thread
threading.Thread(target=check_stock, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
