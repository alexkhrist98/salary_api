import os

import fastapi
import psycopg2
import dotenv
import asyncio
import logging
import hashlib
import app.models as models
from main import logger
import asyncpg


dotenv.load('/root/.env')
DB_USER = os.getenv('DB_USER')
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
API_ADMIN_LOGIN = os.getenv('API_ADMIN_LOGIN')
API_ADMIN_PASSWORD = os.getenv('API_ADMIN_PASSWORD')
TABLE_NAME = os.getenv('DB_TABLE_NAME')



async def create_admin(admin_login: str, admin_password: str):
    try:
        hasher = hashlib.sha256()
        hasher.update(admin_password.encode())
        admin_password_hash = hasher.hexdigest()
        logger.info('Password hashed succsesfully')
    except ValueError:
        logger.error('Problems with hashing function')
    except AttributeError:
        logging.error('Invalid password submitted for hashing. Password should be str')

    try:
        async with pool.acquire() as conn:
            await conn.execute('BEGIN')
            await conn.execute(f'INSERT INTO {TABLE_NAME} VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING', admin_login, admin_password_hash, 0.0, "NEVER")
            await conn.execute('COMMIT')
        logging.info('Admin created sucesfully')
    except:
        logging.error('SOmething went wrong')
        logger.exception('An eception has occured \m %s')

async def fetch_user(user: models.User):
    try:
        async with pool.acquire() as conn:
            await conn.execute('BEGIN')
            user_data = await conn.fetchrow(f"SELECT * FROM {TABLE_NAME} WHERE user_name = $1", user.user_name)
            await conn.execute('COMMIT')

        user_data = dict(user_data)
        user = models.Employee.parse_obj(user_data)
        logger.info('User fetched')
        return user
    except:
        logging.exception('An exception has occured \m %s')

async def create_employee(employee: models.Employee):
    try:
        async with pool.acquire() as conn:
            conn.transaction()
            await conn.execute(f'INSERT INTO {TABLE_NAME} VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING', employee.user_name, employee.password, employee.salary, employee.promotion_date)
    except Exception:
        logger.exception("An exception has occured")
        return fastapi.HTTPException(status_code=500)

async def create_pool():
    global pool
    pool = await asyncpg.create_pool(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    asyncio.create_task(create_admin(API_ADMIN_LOGIN, API_ADMIN_PASSWORD))


async def delete_employee(employee: models.Employee):
    try:
        async with pool.acquire() as conn:
            conn.transaction()
            await conn.execute(F'DELETE FROM {TABLE_NAME} WHERE user_name = $1', employee.user_name)
            logger.info("User deleted")
    except asyncpg.InvalidGrantOperationError:
        logger.exception("An exception has occured")

async def update_employee(employee: models.Employee):

    async with pool.acquire() as conn:
        conn.transaction()
        await conn.execute(f'UPDATE {TABLE_NAME} SET salary = $1, promotion_date = $2 WHERE user_name = $3 AND salary IS NOT NULL AND promotion_date IS NOT NULL', employee.salary, employee.promotion_date, employee.user_name)
        logger.info('User updated')


if __name__ != "__main__":
    asyncio.create_task(create_pool())

