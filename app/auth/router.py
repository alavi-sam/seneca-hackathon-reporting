from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.services import get_user, create_access_token, validate_user



auth_router = APIRouter()
static_templates = Jinja2Templates(directory='app/statics')


@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return static_templates.TemplateResponse("login.html", {"request": request})


@auth_router.post('/login')
async def login_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    fetched_user = get_user(db, form_data.username)
    if not fetched_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = validate_user(db, fetched_user, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={'sub': user.username})
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key = "access_token",
        value = f"Bearer {access_token}",
        httponly = True,
        samesite= "lax"
    )
    return response

    