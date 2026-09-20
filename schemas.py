from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    name: str
    email: str
    age: int = 18
    bio: str = ""
    image_url: str = ""
    extra_photos: List[str] = []
    interests: List[str] = []


class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    bio: str
    image_url: str
    extra_photos: List[str]
    interests: List[str]
    coins: int
    is_banned: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    extra_photos: Optional[List[str]] = None
    interests: Optional[List[str]] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageCreate(BaseModel):
    receiver_id: int
    content: str
    type: str = "text"
    gift_coins: int = 0


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    type: str
    gift_coins: int
    is_admin_message: bool
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price_coins: int
    category: str = "feature"
    image_url: str = ""


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price_coins: int
    category: str
    image_url: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    amount: int
    type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    product_id: int


class NoteCreate(BaseModel):
    user_id: int
    content: str


class NoteResponse(BaseModel):
    id: int
    user_id: int
    admin_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class BroadcastRequest(BaseModel):
    message: str