from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
import os
from app.db import get_db
from app.auth.services import get_user
from sqlalchemy.orm import Session
from app.models import ReportUser


# 
def get_current_user(request: Request, db: Session):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        token_data = token.replace("Bearer ", "")
        decoded_token = jwt.decode(token_data, key=os.getenv("AUTH_SECRET"), algorithms=os.getenv("AUTH_ALGORITHM"))
        token_username = decoded_token.get('sub')
        if token_username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        if get_user(db, token_username) is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": token_username}
    except Exception as e:
        print(str(e))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
       