from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from app.db import get_db
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user


def check_for_login(request: Request, db: Session=Depends(get_db)):
    try:
        user = get_current_user(request, db)
        return user
    except:
        return False

