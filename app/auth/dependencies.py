from fastapi import Depends, Request, HTTPException, staticfiles, status
from jose import jwt, JWTError
import os



def get_current_user(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        token_data = token.replace("Bearer ", "")
        decoded_token = jwt.decode(token_data, key=os.getenv("AUTH_SECRET"), algorithms=os.getenv("AUTH_ALGORITHM"))
        token_username = decoded_token.get('sub')
        if token_username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": token_username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
       