import bcrypt, os, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_MINUTES = 30

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(id:int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes = JWT_EXPIRY_MINUTES)
    payload = {'sub': str(id), 'exp': expire}
    return jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'api/auth/login')

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms = [JWT_ALGORITHM])
        return int(payload['sub'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code = 401, detail = 'Token has expired')
    except jwt.InvaludeTokenError:
        raise HTTPException(statud_code = 401, detail = 'Could not validate token')