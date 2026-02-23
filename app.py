"""
=============================================================
  TradingView → Telegram Alert Middleware
  Receives alerts from TradingView and forwards to multiple
  Telegram users with full per-person control
=============================================================
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────
# 🔧 YOUR BOT TOKEN — Change this to your token
# ─────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8582578419:AAH7AreQ3UzohJRm7w9jy12YF4HxYqUQ0YM")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ─────────────────────────────────────────────
# 👥 SUBSCRIBERS LIST
# Each person has:
#   name       : friendly name (for your reference)
#   chat_id    : their Telegram chat ID
#   active     : True = receives alerts, False = paused
#   strategy   : "ALL" = all alerts, or specific name like "SIB" / "NIFTY"
# ─────────────────────────────────────────────
SUBSCRIBERS = [
    {
        "name": "Balusamy (Owner)",
        "chat_id": "1793471750",       # ← Your chat ID
        "active": True,
        "strategy": "ALL"              # receives all alerts
    },
  
  #  {
   #     "name": "Friend 1",
    #    "chat_id": "FRIEND1_CHAT_ID",  # ← Replace with friend's chat ID
     #   "active": True,
      #  "strategy": "ALL"
    #},
  
   # {
    #    "name": "Friend 2",
     #   "chat_id": "FRIEND2_CHAT_ID",  # ← Replace with friend's chat ID
      #  "active": False,               # ← Disabled — won't receive alerts
       # "strategy": "SIB"             # only receives SIB alerts
    #},
  
    # ── Add more people below this line ──
    # {
    #     "name": "Friend 3",
    #     "chat_id": "FRIEND3_CHAT_ID",
    #     "active": True,
    #     "strategy": "NIFTY"
    # },
]

# ─────────────────────────────────────────────
# 🔐 SECRET KEY — TradingView will send this
# to verify the request is from you
# ─────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey123")


def send_telegram_message(chat_id, text):
    """Send a message to one Telegram chat ID"""
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        result = response.json()
        if result.get("ok"):
            return True, "Sent"
        else:
            return False, result.get("description", "Unknown error")
    except Exception as e:
        return False, str(e)


def forward_to_all(alert_text, strategy_name="ALL"):
    """Forward alert to all active subscribers"""
    results = []
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    for person in SUBSCRIBERS:
        # Skip if person is disabled
        if not person["active"]:
            results.append(f"⏸ SKIPPED: {person['name']} (disabled)")
            continue

        # Skip if strategy doesn't match
        if person["strategy"] != "ALL" and person["strategy"] != strategy_name:
            results.append(f"⏭ SKIPPED: {person['name']} (strategy filter)")
            continue

        # Send the alert
        success, msg = send_telegram_message(person["chat_id"], alert_text)

        if success:
            results.append(f"✅ SENT: {person['name']}")
        else:
            results.append(f"❌ FAILED: {person['name']} — {msg}")

    # Log to console
    print(f"\n[{timestamp}] Alert forwarded:")
    print(f"Message: {alert_text[:80]}...")
    for r in results:
        print(f"  {r}")

    return results


# ─────────────────────────────────────────────
# 📡 WEBHOOK ENDPOINT
# TradingView will POST alerts to this URL
# ─────────────────────────────────────────────
@app.route("/alert", methods=["POST"])
def receive_alert():
    """Receive alert from TradingView and forward to subscribers"""

    # Optional: verify secret key
    incoming_key = request.headers.get("X-Secret-Key", "")
    if incoming_key != SECRET_KEY:
        # If you don't want to use secret key, comment out these 2 lines
        pass  # Remove 'pass' and uncomment below to enforce security
        # return jsonify({"error": "Unauthorized"}), 401

    try:
        # Parse the incoming JSON from TradingView
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extract fields from TradingView alert
        text = data.get("text", "No message")
        strategy = data.get("strategy", "ALL")  # optional strategy filter

        # Format the final message
        timestamp = datetime.now().strftime("%d-%b %H:%M")
        formatted_message = f"{text}\n\n🕐 _{timestamp} IST_"

        # Forward to all matching subscribers
        results = forward_to_all(formatted_message, strategy)

        return jsonify({
            "status": "ok",
            "forwarded": len([r for r in results if "✅" in r]),
            "skipped": len([r for r in results if "SKIPPED" in r]),
            "failed": len([r for r in results if "❌" in r]),
            "details": results
        }), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 📋 STATUS PAGE — Visit your URL to check
# ─────────────────────────────────────────────
@app.route("/", methods=["GET"])
def status():
    """Shows current subscriber status"""
    active = [p for p in SUBSCRIBERS if p["active"]]
    inactive = [p for p in SUBSCRIBERS if not p["active"]]

    return jsonify({
        "status": "🟢 Server Running",
        "total_subscribers": len(SUBSCRIBERS),
        "active": len(active),
        "inactive": len(inactive),
        "subscribers": [
            {
                "name": p["name"],
                "active": p["active"],
                "strategy": p["strategy"]
            }
            for p in SUBSCRIBERS
        ]
    })


# ─────────────────────────────────────────────
# 🧪 TEST ENDPOINT — Send test alert manually
# Visit: yourdomain.com/test
# ─────────────────────────────────────────────
@app.route("/test", methods=["GET"])
def test_alert():
    """Send a test alert to all active subscribers"""
    test_message = (
        "🧪 *TEST ALERT*\n\n"
        "✅ Your middleware is working!\n"
        "📡 TradingView → Python → Telegram\n\n"
        "This is a test message from your alert server."
    )
    results = forward_to_all(test_message, "ALL")
    return jsonify({"status": "Test sent", "results": results})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Alert Middleware running on port {port}")
    print(f"📡 Webhook URL: http://localhost:{port}/alert")
    print(f"📋 Status URL: http://localhost:{port}/")
    app.run(host="0.0.0.0", port=port, debug=False)
