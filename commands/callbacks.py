# Keeps the original callback names from the supplied source in one place.
# Business logic is routed to the modular command modules.

from commands.user import leaderboard, my_referral, daily_reward, top_balance, status, join_checker
from commands.withdraw import approve, reject

ORIGINAL_CALLBACKS = {
    "leaderboard": leaderboard,
    "top_ref": None,
    "daily_reward": daily_reward,
    "my_referral": my_referral,
    "top_balance": top_balance,
    "status": status,
    "reject": reject,
    "continue": approve,
    "top_withdraw": None,
    "delete_leaderboard_message": None,
    "manage_panel_giftcode": None,
    "change_ref": None, "set_bonus": None, "earn_text_set": None,
    "change_mini": None, "change_max": None, "change_refer_text": None,
    "change_tax": None, "gateway_url_change": None, "add_admin": None,
    "remove_admin": None, "change_fund": None, "max_payout": None,
    "change_balance": None, "verify_user": None, "create_gf": None,
    "get_details": None, "back_btn": None, "bot_status": None,
    "with_status": None, "device_auth_toggle": None, "auth_ui_theme": None,
    "change_cha": None, "broad_pane": None, "add_cha": None,
    "add_pay_cha": None, "broad_master_xxx": None, "broad_master_yyy": None,
    "pay_cha": None, "pay_comment": None, "stop_broadcast": None,
    "change_wallet": None, "claim_bonus": None, "join_checker": join_checker,
    "a_giftcode": None,
}
