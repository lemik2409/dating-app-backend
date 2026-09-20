from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Product, Transaction, Message, Note
from schemas import (
    UserResponse, ProductResponse, TransactionResponse,
    BroadcastRequest, NoteCreate, NoteResponse, UserUpdate
)
from auth import get_current_admin
from routers.auth_router import user_to_response

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============================================================
# USERS
# ============================================================

@router.get("/users", response_model=List[UserResponse])
def all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = db.query(User).all()
    return [user_to_response(u) for u in users]


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User nicht gefunden")

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.age is not None:
        user.age = data.age
    if data.bio is not None:
        user.bio = data.bio
    if data.image_url is not None:
        user.image_url = data.image_url
    if data.extra_photos is not None:
        user.extra_photos = ",".join(data.extra_photos)
    if data.interests is not None:
        user.interests = ",".join(data.interests)

    db.commit()
    db.refresh(user)
    return user_to_response(user)


@router.post("/users/{user_id}/ban")
def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User nicht gefunden")
    user.is_banned = not user.is_banned
    db.commit()
    return {"is_banned": user.is_banned}


@router.post("/users/{user_id}/add-coins")
def admin_add_coins(
    user_id: int,
    amount: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User nicht gefunden")

    user.coins += amount

    tx = Transaction(
        user_id=user.id,
        user_name=user.name,
        amount=amount,
        type="bonus",
        status="completed",
    )
    db.add(tx)
    db.commit()
    db.refresh(user)
    return {"coins": user.coins}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User nicht gefunden")
    db.delete(user)
    db.commit()
    return {"ok": True}


# ============================================================
# TRANSAKTIONEN
# ============================================================

@router.get("/transactions", response_model=List[TransactionResponse])
def all_transactions(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).all()


# ============================================================
# BROADCAST
# ============================================================

@router.post("/broadcast")
def broadcast(
    data: BroadcastRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = db.query(User).all()
    for user in users:
        msg = Message(
            sender_id=admin.id,
            receiver_id=user.id,
            content=data.message,
            type="text",
            is_admin_message=True,
        )
        db.add(msg)
    db.commit()
    return {"sent_to": len(users)}


# ============================================================
# STATS
# ============================================================

@router.get("/stats")
def stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return {
        "total_users": db.query(User).count(),
        "total_coins": sum(u.coins for u in db.query(User).all()),
        "total_transactions": db.query(Transaction).count(),
        "total_messages": db.query(Message).count(),
    }


# ============================================================
# NOTIZEN
# ============================================================

@router.get("/notes/{user_id}", response_model=List[NoteResponse])
def get_notes(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(Note).filter(
        Note.user_id == user_id,
        Note.admin_id == admin.id
    ).order_by(Note.created_at.desc()).all()


@router.post("/notes", response_model=NoteResponse)
def create_note(
    data: NoteCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    note = Note(
        user_id=data.user_id,
        admin_id=admin.id,
        content=data.content,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(404, "Notiz nicht gefunden")
    db.delete(note)
    db.commit()
    return {"ok": True}