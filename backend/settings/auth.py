
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from settings.config import secret
from schemas.users import CurUser
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth= OAuth2PasswordBearer(tokenUrl="user/login")
#jwt token code here
def genToken(data:dict):
    data_temp= data.copy()
    data_temp['exp'] = datetime.now(timezone.utc) + timedelta(minutes= secret.access_token_expire_minutes)
    token= jwt.encode(data_temp, secret.secret_key, algorithm= secret.algorithm)
    return token
    

def authenticate(token= Depends(oauth)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data= jwt.decode(token, secret.secret_key, algorithms=[secret.algorithm])
        if token_data['user_id'] is None:
            raise credentials_exception
        return CurUser(**token_data)
    except Exception as e:
        print(e)
        raise credentials_exception
    
def adminAuthenticate(token= Depends(oauth)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    permissions_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )
    permissions= False
    try:
        token_data= jwt.decode(token, secret.secret_key, algorithms=[secret.algorithm])
        if token_data['email'] is None:
            raise credentials_exception
        user= CurUser(**token_data)
        if user.role_id not in [secret.admin_role, secret.s_admin_role]:
            permissions= True
            raise permissions_exception
        return user
    except:
        if permissions:
            raise permissions_exception
        else:
            raise credentials_exception

def encrypt(pwd):
    return pwd_context.hash(pwd)

def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)