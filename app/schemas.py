from pydantic import BaseModel
from datetime import datetime
from app.models import UserRole

class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    owner: UserResponse

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    owner: UserResponse

    model_config = {"from_attributes": True}
    