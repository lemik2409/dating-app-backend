from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Message
from schemas import MessageCreate, MessageResponse
from auth import get_current_user

router = APIRouter(prefix="/api/chats", tags=["Chats"])


@router.get("/{other_user_id}", response_model=List[MessageResponse])
def get_messages(
    other_user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.sender_id == current.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current.id))
    ).order_by(Message.created_at).all()
    return messages


@router.post("/send", response_model=MessageResponse)
def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    msg = Message(
        sender_id=current.id,
        receiver_id=data.receiver_id,
        content=data.content,
        type=data.type,
        gift_coins=data.gift_coins,
        is_admin_message=current.is_admin,
    )
    db.add(msg)

    if data.type == "gift" and data.gift_coins > 0:
        if current.coins >= data.gift_coins:
            current.coins -= data.gift_coins
            receiver = db.query(User).filter(User.id == data.receiver_id).first()
            if receiver:
                receiver.coins += data.gift_coins

    db.commit()
    db.refresh(msg)
    return msg