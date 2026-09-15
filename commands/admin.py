from utils.db import get_db, admin_doc
from utils.helpers import is_admin
from utils.ui import inline

INPUT_ACTIONS={
    "change_ref":("ref","💰 Send new referral reward:"),
    "set_bonus":("bonus","🎁 Send new daily bonus:"),
    "change_mini":("mini","📉 Send minimum withdrawal:"),
    "change_max":("max","📈 Send maximum withdrawal:"),
    "change_tax":("tax","💸 Send tax percentage:"),
    "change_fund":("max_funds","💰 Send maximum funds:"),
    "max_payout":("max_payout","💵 Send maximum payout:"),
    "change_refer_text":("refer_text","📝 Send new leaderboard text:"),
    "earn_text_set":("earn_text","📝 Send new earn text:"),
    "gateway_url_change":("gatewayurl","🔗 Send gateway URL:"),
    "add_admin":("add_admin","👑 Send Telegram user ID to add:"),
    "remove_admin":("remove_admin","🗑 Send Telegram user ID to remove:"),
    "change_balance":("change_balance","💰 Send: USER_ID AMOUNT"),
    "get_details":("get_details","🔍 Send Telegram user ID:"),
    "add_cha":("add_cha","📢 Send channel username or ID:"),
    "rcha":("rcha","📢 Send channel username or ID to remove:"),
    "pay_cha":("paycha","📢 Send payment notification channel:"),
    "pay_comment":("comment","📝 Send payment comment:"),
}

def panel_keyboard():
    return inline([
        [("Change Refer","change_ref"),("Set Bonus","set_bonus")],
        [("Change Minimum","change_mini"),("Change Maximum","change_max")],
        [("Change Tax","change_tax"),("Change Funds","change_fund")],
        [("Max Payout","max_payout"),("Refer Text","change_refer_text")],
        [("Earn Text","earn_text_set"),("Gateway URL","gateway_url_change")],
        [("Add Admin","add_admin"),("Remove Admin","remove_admin")],
        [("Add Balance","change_balance"),("Get User Info","get_details")],
        [("Bot Status","bot_status"),("Withdrawals","with_status")],
        [("Broadcast Panel","broad_pane"),("Channels","change_cha")],
        [("Add Channel","add_cha"),("Remove Channel","rcha")],
        [("Payment Channel","pay_cha"),("Payment Comment","pay_comment")],
        [("Bot Current Stats","status"),("Top Referrers","top_ref")],
        [("Top Withdrawals","top_withdraw"),("Top Balance","top_balance")],
        [("Create Gift Code","manage_panel_giftcode")],
        [("🔒 Device Auth","device_auth_toggle"),("🎨 Auth UI","auth_ui_theme")],
    ])

async def panel(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not an admin."); return
    d=admin_doc()
    await update.message.reply_text(
        f"👑 Welcome To Admin Panel\n\n"
        f"📊 Bot Current Stats\n"
        f"💰 Per Refer: {d.get('ref')} INR\n"
        f"🎁 Daily Bonus: {d.get('bonus')} INR\n"
        f"📉 Minimum Withdraw: {d.get('mini')} INR\n"
        f"📈 Maximum Withdraw: {d.get('max')} INR\n"
        f"💸 Tax: {d.get('tax')}%\n"
        f"🤖 Bot Status: {d.get('botstat')}\n"
        f"💸 Withdrawals: {d.get('withstat')}\n"
        f"🔒 Device Auth: {d.get('device_auth')}\n"
        f"🎨 Auth UI: {str(d.get('auth_ui_theme','v1')).upper()}",
        reply_markup=panel_keyboard())

async def callback(update, context):
    q=update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    a=q.data; db=get_db(); d=admin_doc()
    toggles={
        "bot_status":("botstat","On","Off"),
        "with_status":("withstat","On","Off"),
        "device_auth_toggle":("device_auth","On","Off"),
    }
    if a in toggles:
        field,on,off=toggles[a]
        db.admin.update_one({"admin":"admin"},{"$set":{field:off if d.get(field)==on else on}})
        await panel(update,context); return
    if a=="auth_ui_theme":
        db.admin.update_one({"admin":"admin"},{"$set":{"auth_ui_theme":"v2" if d.get("auth_ui_theme","v1")=="v1" else "v1"}})
        await panel(update,context); return
    if a in ("top_balance","status","top_ref","top_withdraw"):
        if a=="status":
            await q.message.reply_text(f"📊 Users: {db.info.count_documents({})}\nWithdraw records: {db.withdraw.count_documents({})}")
        elif a=="top_balance":
            rows=list(db.info.find().sort("balance",-1).limit(10))
            await q.message.reply_text("💰 Top Balance\n\n"+"\n".join(f"{i}. {x.get('user')} — {float(x.get('balance',0)):.2f}" for i,x in enumerate(rows,1)))
        elif a=="top_ref":
            rows=list(db.refer.aggregate([{"$match":{"invited":{"$type":"number"}}},{"$group":{"_id":"$invited","n":{"$sum":1}}},{"$sort":{"n":-1}},{"$limit":10}]))
            await q.message.reply_text("🏆 Top Referrers\n\n"+"\n".join(f"{i}. {x['_id']} — {x['n']}" for i,x in enumerate(rows,1)))
        else:
            rows=list(db.withdraw.find().sort("toWith",-1).limit(10))
            await q.message.reply_text("💸 Top Withdrawals\n\n"+"\n".join(f"{i}. {x.get('user')} — {float(x.get('toWith',0)):.2f}" for i,x in enumerate(rows,1)))
        return
    if a=="manage_panel_giftcode":
        context.user_data["admin_input"]="create_gift"
        await q.message.reply_text("🎁 Send: CLAIMS AMOUNT"); return
    if a in ("broad_pane","broad_master_xxx","broad_master_yyy"):
        context.user_data["broadcast_waiting"]=True
        await q.message.reply_text("📣 Send the message/media to broadcast."); return
    if a in INPUT_ACTIONS:
        context.user_data["admin_input"]=a
        await q.message.reply_text(INPUT_ACTIONS[a][1]); return
    if a=="change_cha":
        chans=d.get("channels",[]) or []
        await q.message.reply_text("📢 Required Channels:\n\n" + ("\n".join(map(str,chans)) if chans else "None"))
        return
    if a=="back_btn":
        await panel(update,context); return
    if a in ("claim_bonus","join_checker","leaderboard","daily_reward","my_referral"):
        return

async def text(update, context):
    if not is_admin(update.effective_user.id): return False
    a=context.user_data.get("admin_input")
    if not a: return False
    t=update.message.text.strip(); db=get_db()
    try:
        if a in ("change_ref","set_bonus","change_mini","change_max","change_tax","change_fund","max_payout"):
            field=INPUT_ACTIONS[a][0]; db.admin.update_one({"admin":"admin"},{"$set":{field:float(t)}})
        elif a in ("change_refer_text","earn_text_set","gateway_url_change","pay_cha","pay_comment"):
            field=INPUT_ACTIONS[a][0]; db.admin.update_one({"admin":"admin"},{"$set":{field:t}})
        elif a=="add_admin":
            db.admin.update_one({},{"$addToSet":{"admins":int(t)}},upsert=True)
        elif a=="remove_admin":
            db.admin.update_one({},{"$pull":{"admins":int(t)}})
        elif a=="change_balance":
            uid,amount=t.split()[:2]; db.info.update_one({"user":int(uid)},{"$inc":{"balance":float(amount)}},upsert=True)
        elif a=="get_details":
            uid=int(t); x=db.info.find_one({"user":uid}) or {}
            await update.message.reply_text(f"👤 User: {uid}\n💰 Balance: {float(x.get('balance',0)):.2f}\n💳 UPI: {x.get('wallet','NOT SET')}\n✅ Verified: {x.get('verified',False)}")
        elif a=="add_cha":
            db.admin.update_one({"admin":"admin"},{"$addToSet":{"channels":t}})
        elif a=="rcha":
            db.admin.update_one({"admin":"admin"},{"$pull":{"channels":t}})
        elif a=="create_gift":
            parts=t.split(); claims=int(parts[0]); amount=float(parts[1])
            import secrets,string
            code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(10))
            db.giftcodes.insert_one({"code":code,"remaining_claims":claims,"amount":amount,"claimed_by":[]})
            await update.message.reply_text(f"🎁 Gift Code: `{code}`",parse_mode="Markdown")
        context.user_data.pop("admin_input",None)
        if a!="get_details" and a!="create_gift":
            await update.message.reply_text("✅ Updated successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid input: {e}")
    return True
