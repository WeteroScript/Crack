import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# Загружаем переменные окружения из Bothost
load_dotenv()

# Импорты из наших файлов (db.py, routes.py, bot.py)
from db import Base, engine
from routes import router
from bot import dp, BOT_TOKEN
from aiogram import Bot

# Настройка логирования, чтобы видеть, что происходит в Bothost
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BothostApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Инициализация базы данных
    logger.info("Starting up: initializing database...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Запуск Telegram-бота в фоне
    logger.info("Starting up: launching aiogram bot...")
    if not BOT_TOKEN or BOT_TOKEN == "change-me":
        logger.error("❌ BOT_TOKEN is missing or invalid! Bot will not start.")
    else:
        bot = Bot(BOT_TOKEN)
        # Создаем фоновую задачу для Long Polling
        task = asyncio.create_task(dp.start_polling(bot))
        logger.info("✅ Bot polling task created.")
    
    yield # Приложение работает
    
    # 3. Корректная остановка
    logger.info("Shutting down...")
    if 'task' in locals():
        task.cancel()
    if 'bot' in locals():
        await bot.session.close()

# Создаем FastAPI приложение с нашим lifespan
app = FastAPI(lifespan=lifespan, title="Key Verify Bot")

# Подключаем API роуты (проверка ключей, админка)
app.include_router(router)

# Эндпоинт для проверки здоровья (Bothost стучится сюда)
@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "key-verify-bot"}

# =======================================================================
# ⚠️ САМЫЙ ВАЖНЫЙ БЛОК ДЛЯ BOTHOST
# Так как Bothost сам вызывает python main.py, мы запускаем Uvicorn сами.
# Порт берем из переменной окружения (Bothost выдает 3000), иначе 3000.
# =======================================================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    logger.info(f"🚀 Starting Uvicorn on host 0.0.0.0, port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
