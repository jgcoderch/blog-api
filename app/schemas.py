from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        if not any(char.isdigit() for char in value):
            raise ValueError("A senha deve conter pelo menos um número")
        if not any(char.isalpha() for char in value):
            raise ValueError("A senha deve conter pelo menos uma letra")
        return value
        
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
    