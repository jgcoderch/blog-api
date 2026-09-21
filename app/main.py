from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.models import UserRole
from app.schemas import UserCreate, UserResponse, Token, PostCreate, PostResponse, CommentCreate, CommentResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    register_failed_login,
    reset_failed_login,
    get_lockout_seconds_remaining,
)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    new_user = models.User(email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        lockout_seconds = get_lockout_seconds_remaining(user)
        if lockout_seconds > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas tentativas de login. Tente novamente em {lockout_seconds} segundos.",
            )

    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            register_failed_login(db, user)
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    reset_failed_login(db, user)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


def check_permission(resource_owner_id: int, current_user: models.User):
    if current_user.role != UserRole.admin and current_user.id != resource_owner_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para essa ação")


@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_post = models.Post(title=post.title, content=post.content, owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts", response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    return post


@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, updated: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado")

    check_permission(post.owner_id, current_user)

    post.title = updated.title
    post.content = updated.content
    db.commit()
    db.refresh(post)
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado")

    check_permission(post.owner_id, current_user)

    db.delete(post)
    db.commit()
    return None

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado")

    new_comment = models.Comment(content=comment.content, post_id=post_id, owner_id=current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()


@app.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")

    check_permission(comment.owner_id, current_user)

    db.delete(comment)
    db.commit()
    return None