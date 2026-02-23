# 📡 TradingView → Telegram Alert Middleware

Receives alerts from TradingView and forwards to multiple Telegram users.

---

## 🚀 DEPLOY TO RAILWAY (Step by Step)

### Step 1: Upload to GitHub
1. Go to github.com → Create new repository → Name it `sib-alert-bot`
2. Upload these 4 files: `app.py`, `requirements.txt`, `Procfile`, `README.md`

### Step 2: Deploy on Railway
1. Go to railway.app → Sign up free with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `sib-alert-bot` repo
4. Railway will auto-detect and deploy ✅

### Step 3: Set Environment Variables on Railway
In Railway dashboard → Your project → Variables tab, add:
```
BOT_TOKEN = your_actual_bot_token_here
SECRET_KEY = any_password_you_choose
```

### Step 4: Get Your Public URL
Railway gives you a URL like:
`https://sib-alert-bot-production.up.railway.app`

### Step 5: Test It
Visit: `https://your-railway-url.up.railway.app/test`
You should receive a test Telegram message ✅

---

## 📱 HOW TO GET SOMEONE'S CHAT ID

Ask your friend to:
1. Open Telegram → Search `@userinfobot`
2. Press START or send any message
3. Bot replies with their chat ID number
4. Share that number with you

---

## ⚙️ TRADINGVIEW WEBHOOK SETUP

In TradingView Alert settings:
- **Webhook URL**: `https://your-railway-url.up.railway.app/alert`
- **Message Body**:
```json
{
  "text": "🚨 *SIB Alert*\n\n{{strategy.order.comment}}\n💰 Price: {{close}}\n📊 Action: {{strategy.order.action}}",
  "strategy": "SIB"
}
```

---

## 👥 ADD / REMOVE PEOPLE (in app.py)

```python
# ADD a new person:
{
    "name": "New Friend",
    "chat_id": "THEIR_CHAT_ID",
    "active": True,          # True = gets alerts
    "strategy": "ALL"        # ALL or specific like "SIB" / "NIFTY"
},

# DISABLE someone (stop alerts without deleting):
"active": False

# Only send specific strategy alerts:
"strategy": "SIB"    # only SIB alerts
"strategy": "NIFTY"  # only NIFTY alerts
"strategy": "ALL"    # all alerts
```

---

## 📋 USEFUL URLS

| URL | Purpose |
|-----|---------|
| `yourdomain.com/` | Check server status + subscriber list |
| `yourdomain.com/test` | Send test alert to everyone |
| `yourdomain.com/alert` | TradingView webhook (POST) |
