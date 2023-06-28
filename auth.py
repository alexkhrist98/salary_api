import fastapi
import jwt
import app.models as models
import dotenv
import os
import asyncio
import hashlib
from main import logger
import time
import pydantic
import app.db_logic as db_logic

dotenv.load('/root/.env')
SECRET_KEY = os.getenv('SECRET_KEY')
API_ADMIN_LOGIN = os.getenv("API_ADMIN_LOGIN")
API_ADMIN_PASSWORD = os.getenv('API_ADMIN_PASSWORD')
async def hash_password(pwd: str):

    hasher = hashlib.sha256()
    hasher.update(pwd.encode())
    pwd_hash = hasher.hexdigest()
    logger.info('password hashed succesfully')
    return pwd_hash

async def generate_jwt(user: models.User):
    payload = models.Token_payload(user_name=user.user_name,
                                   password=user.password,
                                   exp=(time.time() + 699))
    token = jwt.PyJWT().encode(payload.dict(), key=SECRET_KEY, )
    logger.info('JWT created!')
    print(token)
    return token

async def validate(token: jwt):
   try:
        payload = jwt.PyJWT().decode(token.token_string, SECRET_KEY)
        payload = models.Token_payload.parse_obj(payload)
   except jwt.ExpiredSignatureError:
       return fastapi.HTTPException(status_code=401, detail="Your token has expired")
   employee = await db_logic.fetch_user(models.User(user_name=payload.user_name, password=payload.password))
   if payload.user_name != employee.user_name or payload.password != employee.password:
       raise fastapi.HTTPException(status_code=400, detail="Invalid token or incorrect username and password")
   return True

async def token_to_mode(token: models.Token):
    try:
        payload = jwt.PyJWT().decode(token.token_string, SECRET_KEY)
        payload = models.Token_payload.parse_obj(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise fastapi.HTTPException(status_code=402, detail="Token expired")

async def check_admin_prev(token: str):
    payload = await token_to_mode(models.Token(token_string=token))

    if payload.user_name != API_ADMIN_LOGIN or payload.password != await hash_password(API_ADMIN_PASSWORD):
        raise fastapi.HTTPException(status_code=403)

