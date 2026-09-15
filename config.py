import os

BOT_TOKEN = os.getenv("8832769041:AAGLoFAMKyrr109q2xv4K0qUORKFQUbrL9c", "")
MONGO_URI = os.getenv("mongodb+srv://<db_username>:snsoEx6NSAzOpkyN@cluster0.8g3ysxu.mongodb.net/?appName=Cluster0", "")
MONGO_DB = os.getenv("MONGO_DB", "samrat_earning_bot")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7259626275"))
ADMIN_CHANNEL_ID = os.getenv("-1003649466613", "").strip()
CURRENCY = "INR"

# Normal Unicode emojis are used in keyboard labels.
# Telegram does not allow arbitrary button background colours.
EMOJI = {
    "green": "🟢", "red": "🔴", "blue": "🔵", "yellow": "🟡",
    "account": "👤", "bonus": "🎁", "refer": "👥", "withdraw": "💸",
    "wallet": "💳", "admin": "👑", "settings": "⚙️", "success": "✅",
    "error": "❌", "warning": "⚠️", "gift": "🎟️", "money": "💰",
    "lock": "🔒", "search": "🔍", "stats": "📊", "broadcast": "📣",
    "channel": "📢", "back": "🔙", "cancel": "❌️",
}

# Put your Telegram custom-emoji document IDs here if you want to use
# them in message text. Leave blank to use normal Unicode emojis.
CUSTOM_EMOJI_IDS = {
    "account": "", "bonus": "", "refer": "", "withdraw": "",
    "wallet": "", "admin": "", "settings": "", "success": "",
    "error": "", "warning": "", "gift": "", "money": "", "lock": "",
    "search": "", "stats": "", "broadcast": "", "channel": "",
}
