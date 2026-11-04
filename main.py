import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from db import Base, engine
from routes import router
from bot import dp, BOT_TOKEN
from aiogram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BothostApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: initializing database...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Starting up: launching aiogram bot...")
    if not BOT_TOKEN or BOT_TOKEN == "change-me":
        logger.error("❌ BOT_TOKEN is missing or invalid! Bot will not start.")
    else:
        bot = Bot(BOT_TOKEN)
        task = asyncio.create_task(dp.start_polling(bot))
        logger.info("✅ Bot polling task created.")
    
    yield
    
    logger.info("Shutting down...")
    if 'task' in locals():
        task.cancel()
    if 'bot' in locals():
        await bot.session.close()

app = FastAPI(lifespan=lifespan, title="Key Verify Bot")
app.include_router(router)

@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "key-verify-bot"}

if __name__ == "__main__":
    import uvicorn
    # Берем порт из переменной (Bothost дает 3000)
    port = int(os.getenv("PORT", 3000))
    logger.info(f"🚀 Starting Uvicorn on host 0.0.0.0, port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
