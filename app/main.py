from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from app.auth.dependencies import get_current_user
from app.services.authentication import check_for_login
from jose import JWTError
from sqlalchemy.orm import Session
from app.auth.router import auth_router
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
static_templates = Jinja2Templates(directory='app/statics')



@app.get('/index')
async def get_index(request: Request, user=Depends(check_for_login)):
    if not user:
        return RedirectResponse("/auth/login")
    return HTMLResponse("test")
    


@app.get('/')
async def get_main(request: Request, user=Depends(check_for_login)):
    print(user)
    if not user:
        return RedirectResponse("/auth/login")
    print(user)
    return static_templates.TemplateResponse('main.html',
                                             {"request": request, "user": {"username": user['username']}}
)