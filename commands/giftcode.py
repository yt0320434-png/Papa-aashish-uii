from utils.db import get_db
from utils.helpers import is_admin, make_code
from utils.ui import main_keyboard

async def create(update, context):
    if not is_admin(update.effective_user.id): return
    if len(context.args)!=2:
        await update.message.reply_text("Use: /creategift USERS AMOUNT"); return
    try: users=int(context.args[0]); amount=float(context.args[1])
    except ValueError:
        await update.message.reply_text("⛔️ Invalid values."); return
    if users<1 or amount<=0:
        await update.message.reply_text("⛔️ Values must be positive."); return
    code=make_code()
    get_db().giftcodes.insert_one({"code":code,"remaining_claims":users,"amount":amount,"claimed_by":[]})
    await update.message.reply_text(f"🎁 Gift Code Created\n\n`{code}`\nClaims: {users}\nAmount: {amount:g} INR",parse_mode="Markdown")

async def button(update, context):
    q=update.callback_query; await q.answer()
    context.user_data["gift_wait"]=True
    await q.message.reply_text("🎁 Send Gift Code:",reply_markup=main_keyboard())

async def claim(update, context):
    if not context.user_data.get("gift_wait"): return False
    code=update.message.text.strip().upper()
    db=get_db(); uid=update.effective_user.id
    x=db.giftcodes.find_one({"code":code})
    if not x:
        await update.message.reply_text("❌ Invalid Gift Code."); return True
    if uid in x.get("claimed_by",[]) or int(x.get("remaining_claims",0))<=0:
        await update.message.reply_text("❌ Gift Code unavailable."); return True
    db.info.update_one({"user":uid},{"$inc":{"balance":float(x["amount"])}},upsert=True)
    db.giftcodes.update_one({"code":code},{"$inc":{"remaining_claims":-1},"$push":{"claimed_by":uid}})
    context.user_data.pop("gift_wait",None)
    await update.message.reply_text(f"🎁 Gift Code Claimed: +{float(x['amount']):.2f} INR")
    return True
