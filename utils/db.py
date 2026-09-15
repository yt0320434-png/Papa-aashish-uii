from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, ADMIN_ID

_client = None
_db = None

DEFAULT_ADMIN = {
    "admin": "admin",
    "ref": 1,
    "max_payout": 100,
    "bonus": 0.1,
    "mini": 2,
    "max": 4,
    "max_funds": 1000,
    "gt_name": "Not Set",
    "paycha": "@Username",
    "botstat": "On",
    "withstat": "On",
    "subid": "Not Set",
    "mid": "NOT SET",
    "mkey": "NOT SET",
    "comment": "NOT SET",
    "tax": 0,
    "channels": [],
    "auth_ui_theme": "v1",
    "device_auth": "On",
    "earn_text": "Earn more by referring friends!",
    "refer_text": "Referral Leaderboard",
    "gatewayurl": "",
}

def get_db():
    global _client, _db
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is missing. Add it in Replit Secrets.")
    if _db is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        _db = _client[MONGO_DB]
    return _db

def init_db():
    db = get_db()
    if not db.admin.find_one({"admin": "admin"}):
        db.admin.insert_one(DEFAULT_ADMIN.copy())
    else:
        missing = {k:v for k,v in DEFAULT_ADMIN.items() if k not in db.admin.find_one({"admin":"admin"})}
        if missing:
            db.admin.update_one({"admin":"admin"}, {"$set": missing})
    db.admins.update_one({}, {"$addToSet": {"admins": ADMIN_ID}}, upsert=True)

def admin_doc():
    return get_db().admin.find_one({"admin":"admin"}) or DEFAULT_ADMIN.copy()

def get_admins():
    doc = get_db().admins.find_one({}) or {}
    out = {ADMIN_ID}
    for x in doc.get("admins", []):
        try: out.add(int(x))
        except Exception: pass
    return out
