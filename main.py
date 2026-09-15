import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
from config import BOT_TOKEN, MONGO_URI
from utils.db import init_db
from utils.ui import strip_button, main_keyboard
from commands.user import start, account, bonus, refer, daily_reward, leaderboard, my_referral, top_balance, status, join_checker
from commands.wallet import ask as wallet_ask, save as wallet_save, WALLET
from commands.withdraw import ask as withdraw_ask, process as withdraw_process, approve as withdraw_approve, reject as withdraw_reject, WITHDRAW
from commands.giftcode import create as gift_create, button as gift_button, claim as gift_claim
from commands.admin import panel as admin_panel, callback as admin_callback, text as admin_text
from commands.broadcast import start as broadcast_start, send as broadcast_send

logging.basicConfig(level=logging.INFO)

async def text_router(update, context):
    # Pending gift/broadcast/admin inputs get first priority.
    if await gift_claim(update, context):
        return
    if await broadcast_send(update, context):
        return
    if await admin_text(update, context):
        return
    t=strip_button(update.message.text or "")
    if t=="Account":
        await account(update,context)
    elif t=="Bonus":
        await bonus(update,context)
    elif t=="Refer Earn":
        await refer(update,context)
    # Withdraw and Link UPI are handled by their ConversationHandlers.

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_keyboard())
    return ConversationHandler.END

async def error_handler(update, context):
    logging.exception("Unhandled bot error", exc_info=context.error)

def build_app():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add BOT_TOKEN to your hosting environment variables/secrets.")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is missing. Add your MongoDB Atlas connection string to the hosting environment variables/secrets.")
    init_db()
    app=Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_start))
    app.add_handler(CommandHandler("creategift", gift_create))

    wallet_conv=ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^(?:🟢 |🔵 |🟡 |🔴 )?Link UPI$"),wallet_ask)],
        states={WALLET:[MessageHandler(filters.TEXT & ~filters.COMMAND,wallet_save)]},
        fallbacks=[MessageHandler(filters.Regex(r"^(?:🟢 |🔵 |🟡 |🔴 )?Cancel$"),cancel)],
    )
    withdraw_conv=ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^(?:🟢 |🔵 |🟡 |🔴 )?Withdraw$"),withdraw_ask)],
        states={WITHDRAW:[MessageHandler(filters.TEXT & ~filters.COMMAND,withdraw_process)]},
        fallbacks=[MessageHandler(filters.Regex(r"^(?:🟢 |🔵 |🟡 |🔴 )?Cancel$"),cancel)],
    )
    app.add_handler(wallet_conv)
    app.add_handler(withdraw_conv)

    # User callbacks.
    app.add_handler(CallbackQueryHandler(daily_reward,pattern="^daily_reward$"))
    app.add_handler(CallbackQueryHandler(leaderboard,pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(my_referral,pattern="^my_referral$"))
    app.add_handler(CallbackQueryHandler(join_checker,pattern="^join_checker$"))
    app.add_handler(CallbackQueryHandler(gift_button,pattern="^a_giftcode$"))
    app.add_handler(CallbackQueryHandler(withdraw_approve,pattern="^continue$"))
    app.add_handler(CallbackQueryHandler(withdraw_reject,pattern="^reject$"))

    # Admin callbacks. This broad handler is intentionally after the specific
    # user callbacks above, matching the modular command separation.
    app.add_handler(CallbackQueryHandler(admin_callback))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_router))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND,text_router))
    app.add_error_handler(error_handler)
    return app

if __name__=="__main__":
    build_app().run_polling(allowed_updates=Update.ALL_TYPES)
