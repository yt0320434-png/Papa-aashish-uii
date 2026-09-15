from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from utils.db import get_db, admin_doc
from utils.helpers import user_doc, money
from utils.ui import cancel_keyboard, main_keyboard
from config import ADMIN_CHANNEL_ID

WITHDRAW=200

async def ask(update, context):
    d=admin_doc(); x=user_doc(update.effective_user.id)
    if d.get("withstat")!="On":
        await update.message.reply_text("🔴 Withdrawals are currently OFF."); return ConversationHandler.END
    if not x.get("wallet"):
        await update.message.reply_text("💳 Link UPI first."); return ConversationHandler.END
    if float(x.get("balance",0)) < float(d.get("mini",2)):
        await update.message.reply_text(f"⛔️ Minimum withdrawal is {d.get('mini',2)} INR."); return ConversationHandler.END
    await update.message.reply_text(
        f"💸 Enter amount\nMinimum: {d.get('mini',2)} INR\nMaximum: {d.get('max',4)} INR",
        reply_markup=cancel_keyboard())
    return WITHDRAW

async def process(update, context):
    try: amount=float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("⛔️ Invalid amount."); return WITHDRAW
    d=admin_doc(); x=user_doc(update.effective_user.id); bal=float(x.get("balance",0))
    mini=float(d.get("mini",2)); maximum=float(d.get("max",4))
    if amount<mini or amount>maximum or amount>bal:
        await update.message.reply_text("⛔️ Amount is outside the allowed limit or balance."); return WITHDRAW
    tax=float(d.get("tax",0)); net=amount-(amount*tax/100)
    context.user_data["withdraw_amount"]=amount
    context.user_data["withdraw_net"]=net
    await update.message.reply_text(
        f"💸 Confirm Withdrawal\n\nAmount: {amount:.2f} INR\nTax: {tax:g}%\n"
        f"Net: {net:.2f} INR\nUPI: {x.get('wallet')}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Approve",callback_data="continue"),
            InlineKeyboardButton("❌ Cancel",callback_data="reject")
        ]]))
    return ConversationHandler.END

async def approve(update, context):
    q=update.callback_query; await q.answer()
    amount=context.user_data.pop("withdraw_amount",None)
    net=context.user_data.pop("withdraw_net",None)
    if amount is None:
        await q.message.reply_text("❌ Request expired."); return
    db=get_db(); x=user_doc(q.from_user.id); bal=float(x.get("balance",0))
    if bal<amount:
        await q.message.reply_text("❌ Insufficient balance."); return
    d=admin_doc()
    # Deduct only after basic validation. External gateway HTTP integration
    # can be added through the configured gateway URL.
    db.info.update_one({"user":q.from_user.id},{"$inc":{"balance":-amount}})
    db.withdraw.update_one({"user":q.from_user.id},{
        "$inc":{"toWith":amount},"$set":{"last_amount":amount,"last_status":"pending"}
    },upsert=True)
    await q.message.reply_text(
        f"✅ Withdrawal request submitted.\nNet payout: {net:.2f} INR",
        reply_markup=main_keyboard())
    destination = ADMIN_CHANNEL_ID or d.get("paycha")
    if destination and destination != "@Username":
        try:
            await context.bot.send_message(
                chat_id=destination,
                text=(f"💸 WITHDRAWAL REQUEST\n\n"
                      f"👤 User ID: {q.from_user.id}\n"
                      f"💰 Amount: {amount:.2f} INR\n"
                      f"💵 Net: {net:.2f} INR\n"
                      f"💳 UPI: {x.get('wallet','NOT SET')}")
            )
        except Exception as exc:
            await q.message.reply_text(
                f"⚠️ Request saved, but admin notification failed: {exc}"
            )

async def reject(update, context):
    q=update.callback_query; await q.answer()
    context.user_data.pop("withdraw_amount",None); context.user_data.pop("withdraw_net",None)
    await q.message.reply_text("❌ Withdrawal cancelled.", reply_markup=main_keyboard())
