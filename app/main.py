from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.authentication import check_for_login
from app.auth.router import auth_router
from app.report.router import report_router
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(report_router, prefix='/reporting')
static_templates = Jinja2Templates(directory='app/statics')



@app.get('/index')
async def get_index(request: Request, user=Depends(check_for_login)):
    if not user:
        return RedirectResponse("/auth/login")
    return HTMLResponse("test")
    


@app.get('/')
async def get_main(request: Request, user=Depends(check_for_login)):
    if not user:
        return RedirectResponse("/auth/login")
    return static_templates.TemplateResponse('main.html',
                                             {"request": request, "user": {"username": user['username']}}
)