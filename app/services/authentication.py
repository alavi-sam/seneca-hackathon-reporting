from fastapi import Request
from fastapi.responses import RedirectResponse
from app.auth.dependencies import get_current_user


def check_for_login(request: Request):
    try:
        user = get_current_user(request)
        return user
    except:
        return False

