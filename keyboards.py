from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

def captcha_kb(correct: int) -> InlineKeyboardMarkup:
    opts = {correct}
    while len(opts) < 4:
        opts.add(correct + random.randint(-4, 4))
    opts = list(opts)
    random.shuffle(opts)
    row = [InlineKeyboardButton(text=str(n), callback_data=f"cap:{n}") for n in opts]
    return InlineKeyboardMarkup(inline_keyboard=[row])

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Получить Premium-ключ", callback_data="get_key")],
        [InlineKeyboardButton(text="♻️ Сбросить HWID", callback_data="reset_hwid")],
    ])
