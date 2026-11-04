from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def captcha_kb(correct: int) -> InlineKeyboardMarkup:
    # 4 кнопки, среди них правильный ответ
    import random
    opts = {correct}
    while len(opts) < 4:
        opts.add(correct + random.randint(-4, 4))
    opts = list(opts)
    random.shuffle(opts)
    row = [InlineKeyboardButton(text=str(n), callback_data=f"cap:{n}") for n in opts]
    return InlineKeyboardMarkup(inline_keyboard=[row])

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Получить ключ", callback_data="get_key")],
        [InlineKeyboardButton(text="♻️ Сбросить HWID", callback_data="reset_hwid")],
    ])
