from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, LoginRequest, TokenResponse, UserResponse
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        bio=user.bio or "",
        image_url=user.image_url or "",
        extra_photos=[p for p in (user.extra_photos or "").split(",") if p],
        interests=[i for i in (user.interests or "").split(",") if i],
        coins=user.coins,
        is_banned=user.is_banned,
        is_verified=user.is_verified,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.post("/register", response_model=TokenResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-Mail existiert bereits")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        age=data.age,
        bio=data.bio,
        image_url=data.image_url,
        extra_photos=",".join(data.extra_photos),
        interests=",".join(data.interests),
        coins=50,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user_to_response(user))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Falsche Login-Daten")

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Account gesperrt")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user_to_response(user))