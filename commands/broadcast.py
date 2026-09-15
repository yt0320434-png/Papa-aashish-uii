import asyncio
from utils.db import get_db
from utils.helpers import is_admin

async def start(update, context):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["broadcast_waiting"]=True
    await update.message.reply_text("📣 Send the message/photo/video/file you want to broadcast.")

async def panel(update, context):
    q=update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    context.user_data["broadcast_waiting"]=True
    await q.message.reply_text("📣 Send the message/photo/video/file to broadcast.")

async def send(update, context):
    if not context.user_data.get("broadcast_waiting") or not is_admin(update.effective_user.id):
        return False
    context.user_data.pop("broadcast_waiting",None)
    ids=[x.get("user") for x in get_db().info.find({},{"user":1,"_id":0}) if x.get("user")]
    ok=bad=0
    status=await update.message.reply_text("📣 Broadcasting...")
    for uid in ids:
        try:
            await update.message.copy(chat_id=uid)
            ok+=1
        except Exception:
            bad+=1
        await asyncio.sleep(0.04)
    await status.edit_text(f"✅ Broadcast Complete\n\nSent: {ok}\nErrors: {bad}")
    return True
