import os
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models import Key

router = APIRouter(prefix="/api")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me")

# --- контракт с клиентом (имена полей как в Gson) ---
class VerifyReq(BaseModel):
    androidId: str
    key: str
    deviceName: str

class VerifyResp(BaseModel):
    is_key: bool
    is_subscribed: bool
    is_premium: bool

def require_admin(x_admin_token: str = Header(default="")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "unauthorized")

@router.post("/verify", response_model=VerifyResp)
def verify(req: VerifyReq, db: Session = Depends(get_db)):
    k = db.query(Key).filter(Key.key == req.key).first()

    # нет ключа / неактивен → 404 → клиент: InvalidKey
    if not k or not k.is_active:
        raise HTTPException(404, "invalid_key")

    # привязка к устройству
    if k.android_id is None:
        k.android_id = req.androidId
        k.device_name = req.deviceName
        db.commit()
    elif k.android_id != req.androidId:
        raise HTTPException(403, "android_id_mismatch")  # клиент: AndroidIdMismatch

    # подписка истекла → 200 + is_subscribed=false → клиент: RequireSubscription
    return VerifyResp(
        is_key=True,
        is_subscribed=k.is_subscribed,
        is_premium=k.is_premium,
    )

# --- админка ---
class CreateKeyReq(BaseModel):
    key: str
    is_subscribed: bool = True
    is_premium: bool = False

@router.post("/keys", dependencies=[Depends(require_admin)])
def create_key(body: CreateKeyReq, db: Session = Depends(get_db)):
    if db.query(Key).filter(Key.key == body.key).first():
        raise HTTPException(409, "key exists")
    k = Key(key=body.key, is_subscribed=body.is_subscribed, is_premium=body.is_premium)
    db.add(k); db.commit(); db.refresh(k)
    return {"ok": True, "id": k.id, "key": k.key}

@router.delete("/keys/{key}", dependencies=[Depends(require_admin)])
def revoke_key(key: str, db: Session = Depends(get_db)):
    k = db.query(Key).filter(Key.key == key).first()
    if not k:
        raise HTTPException(404, "not found")
    k.is_active = False
    db.commit()
    return {"ok": True}
