import time
from typing import Dict, Optional
import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()

def token_response(token: str):
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def signJWT(user_id: str, role: str, name: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "role": role,
        "name": name,
        "expires": time.time() + 3600  # Token expires in 1 hour
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decodeJWT(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    token = credentials.credentials
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token.get("expires", 0) >= time.time() else None
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
