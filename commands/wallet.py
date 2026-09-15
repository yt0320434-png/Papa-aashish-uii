from telegram.ext import ConversationHandler
from utils.db import get_db
from utils.ui import cancel_keyboard, main_keyboard

WALLET=100

async def ask(update, context):
    await update.message.reply_text("💳 Send your UPI ID:", reply_markup=cancel_keyboard())
    return WALLET

async def save(update, context):
    t=update.message.text.strip()
    if "@" not in t or len(t)<5:
        await update.message.reply_text("⛔️ Invalid UPI ID. Send again.")
        return WALLET
    get_db().info.update_one({"user":update.effective_user.id},{"$set":{"wallet":t}},upsert=True)
    await update.message.reply_text("✅ UPI ID saved successfully.", reply_markup=main_keyboard())
    return ConversationHandler.END
