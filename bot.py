import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from db import SessionLocal
from models import Key
from keyboards import captcha_kb, main_menu_kb

BOT_TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())

class S(StatesGroup):
    captcha = State()
    menu = State()

# ---------- /start → капча ----------
@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    a, b = random.randint(2, 9), random.randint(2, 9)
    await state.update_data(answer=a + b)
    await state.set_state(S.captcha)
    await msg.answer(f"Подтверди, что ты не бот: сколько будет {a} + {b}?",
                     reply_markup=captcha_kb(a + b))

# ---------- ответ на капчу ----------
@dp.callback_query(S.captcha, F.data.startswith("cap:"))
async def cap_answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if int(cb.data.split(":")[1]) != data.get("answer"):
        a, b = random.randint(2, 9), random.randint(2, 9)
        await state.update_data(answer=a + b)
        await cb.message.edit_text(f"❌ Неверно. Ещё раз: {a} + {b}?",
                                   reply_markup=captcha_kb(a + b))
        return
    await state.set_state(S.menu)
    await cb.message.edit_text("✅ Готово. Главное меню:", reply_markup=main_menu_kb())

# ---------- Получить ключ ----------
@dp.callback_query(F.data == "get_key")
async def get_key(cb: CallbackQuery, state: FSMContext):
    if await state.get_state() != S.menu.state:
        return await cb.answer("Сначала пройди /start", show_alert=True)

    with SessionLocal() as db:
        k = db.execute(select(Key).where(Key.tg_id == cb.from_user.id)).scalar_one_or_none()
        if k and k.is_active:
            return await cb.message.answer(f"У тебя уже есть ключ:\n<code>{k.key}</code>",
                                           parse_mode="HTML")
        
        # Генерируем ровно 12 символов (без дефисов)
        new_key = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
        
        # Создаем ключ (is_premium теперь True по умолчанию из models.py)
        db.add(Key(key=new_key, tg_id=cb.from_user.id))
        db.commit()
        
    await cb.message.answer(f"🔑 Твой Premium-ключ:\n<code>{new_key}</code>\n\n"
                            f"Введи его в приложении.", parse_mode="HTML")

# ---------- Сбросить HWID ----------
@dp.callback_query(F.data == "reset_hwid")
async def reset_hwid(cb: CallbackQuery, state: FSMContext):
    if await state.get_state() != S.menu.state:
        return await cb.answer("Сначала пройди /start", show_alert=True)

    with SessionLocal() as db:
        k = db.execute(select(Key).where(Key.tg_id == cb.from_user.id)).scalar_one_or_none()
        if not k:
            return await cb.message.answer("У тебя ещё нет ключа. Сначала «Получить Premium-ключ».")
        if not k.android_id:
            return await cb.message.answer("HWID и так не привязан.")
            
        k.android_id = None
        k.device_name = None
        db.commit()
        
    await cb.message.answer("♻️ HWID сброшен. Ключ можно активировать на другом устройстве.")
