from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from . import models, schemas, security
from .database import get_db
from typing import List, Optional
from markupsafe import escape

router = APIRouter(prefix="/api", tags=["data"])


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    """
    Dependency to extract current user from Authorization header.
    FastAPI's dependency injection with Depends for header token is done differently in actual code —
    we implement header parsing in the router below to keep code simple and explicit.
    """
    # kept unused — actual check implemented per-route for clarity
    return None


@router.get("/data", response_model=List[schemas.PostOut])
def list_posts(authorization: Optional[str] = Header(None, alias="Authorization"), skip: int = 0, limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    # Auth check
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    token = authorization.split("Bearer ")[1]
    username = security.decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    posts = db.query(models.Post).offset(skip).limit(limit).all()
    # Escape user-controlled fields to mitigate XSS if this data is rendered later in a browser.
    result = []
    for p in posts:
        result.append(schemas.PostOut(
            id=p.id,
            title=escape(p.title),
            content=escape(p.content),
            author=escape(p.author.username if p.author else "unknown")
        ))
    return result


@router.post("/data", response_model=schemas.PostOut)
def create_post(authorization: Optional[str] = Header(None, alias="Authorization"), post_in: schemas.PostCreate = None, db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    token = authorization.split("Bearer ")[1]
    username = security.decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Input was validated by pydantic (PostCreate)
    new_post = models.Post(title=post_in.title, content=post_in.content, author=user)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return schemas.PostOut(
        id=new_post.id,
        title=escape(new_post.title),
        content=escape(new_post.content),
        author=escape(user.username),
    )
