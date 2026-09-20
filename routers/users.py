from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from auth import get_current_user
from routers.auth_router import user_to_response

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/discover", response_model=List[UserResponse])
def discover_users(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    users = db.query(User).filter(
        User.id != current.id,
        User.is_banned == False
    ).all()
    return [user_to_response(u) for u in users]


@router.get("/me", response_model=UserResponse)
def get_me(current: User = Depends(get_current_user)):
    return user_to_response(current)


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    if data.name is not None:
        current.name = data.name
    if data.email is not None:
        current.email = data.email
    if data.age is not None:
        current.age = data.age
    if data.bio is not None:
        current.bio = data.bio
    if data.image_url is not None:
        current.image_url = data.image_url
    if data.extra_photos is not None:
        current.extra_photos = ",".join(data.extra_photos)
    if data.interests is not None:
        current.interests = ",".join(data.interests)

    db.commit()
    db.refresh(current)
    return user_to_response(current)