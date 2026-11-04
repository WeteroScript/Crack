from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Key(Base):
    __tablename__ = "keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    tg_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    android_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)
    # ВОТ ЗДЕСЬ МЕНЯЕМ НА TRUE:
    is_premium: Mapped[bool] = mapped_column(Boolean, default=True) 
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
