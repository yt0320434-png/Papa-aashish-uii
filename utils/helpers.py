import html, time, random, string
from config import ADMIN_ID
from utils.db import get_db, admin_doc, get_admins

def is_admin(uid):
    return int(uid) in get_admins()

def ensure_user(uid, first_name=""):
    db = get_db()
    db.info.update_one({"user": int(uid)}, {
        "$setOnInsert": {"user": int(uid), "balance": 0, "first_name": first_name, "verified": False}
    }, upsert=True)
    db.withdraw.update_one({"user": int(uid)}, {"$setOnInsert": {"user": int(uid), "toWith": 0}}, upsert=True)
    db.refer.update_one({"user": int(uid)}, {"$setOnInsert": {"user": int(uid), "invited": "None", "kid": True}}, upsert=True)

def user_doc(uid):
    ensure_user(uid)
    return get_db().info.find_one({"user":int(uid)}) or {"user":int(uid),"balance":0}

def add_balance(uid, amount):
    get_db().info.update_one({"user":int(uid)}, {"$inc":{"balance":float(amount)}}, upsert=True)

def make_code(n=10):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def money(v):
    return f"{float(v):.2f} INR"

def esc(s):
    return html.escape(str(s))

def now():
    return int(time.time())
