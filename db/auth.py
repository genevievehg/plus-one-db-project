import bcrypt, os, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

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

