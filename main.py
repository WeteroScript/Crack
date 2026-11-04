import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
from db import Base, engine
from routes import router
from bot import dp, BOT_TOKEN
from aiogram import Bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    bot = Bot(BOT_TOKEN)
    task = asyncio.create_task(dp.start_polling(bot))
    yield
    task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
