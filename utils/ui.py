from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import EMOJI

def b(label, colour="blue"):
    return f"{EMOJI.get(colour,'🔵')} {label}"

def main_keyboard():
    return ReplyKeyboardMarkup([
        [b("Account","green"), b("Bonus","yellow")],
        [b("Refer Earn","blue"), b("Withdraw","red")],
        [b("Link UPI","green")],
    ], resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([[b("Cancel","red")]], resize_keyboard=True)

def inline(rows):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b(label, ["green","blue","yellow","red"][i%4]), callback_data=data)
         for i,(label,data) in enumerate(row)]
        for row in rows
    ])

def strip_button(text):
    for e in ("🟢 ","🔵 ","🟡 ","🔴 "):
        if text.startswith(e):
            return text[len(e):]
    return text
