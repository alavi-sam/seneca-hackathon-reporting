from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.services import get_user, create_access_token
from app.auth.dependencies import get_current_user


auth_router = APIRouter()
auth_templates = Jinja2Templates(directory='app/auth/static')


@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return auth_templates.TemplateResponse("login.html", {"request": request})


@auth_router.post('/login')
async def login_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={'sub': user.username})
    response = RedirectResponse(url='/main', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key = "access_token",
        value = f"Bearer {access_token}",
        httponly = True,
        samesite= "lax"
    )
    return response


# @auth_router.get('/index', response_class=HTMLResponse)
# async def index_page(request: Request, user: dict = Depends(get_current_user)):
#     return auth_templates.TemplateResponse("index.html", {"request": request, "username": user["username"]})
    