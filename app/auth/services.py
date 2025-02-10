from sqlalchemy.orm import Session
from app.models import ReportUser
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status
import os



def get_user(db: Session, username: str):
    fetched_user = db.query(ReportUser).filter(ReportUser.username == username).first()
    if fetched_user:
        return fetched_user
    return None


def validate_user(db:Session, user: ReportUser, password: str):
    if user.password == password:
        return user
    return None


def create_access_token(data: dict, expiration_time: timedelta = timedelta(days=1)):
    to_encode = data.copy()
    expire = datetime.now() + expiration_time
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, key=os.getenv("AUTH_SECRET"), algorithm=os.getenv("AUTH_ALGORITHM"))
