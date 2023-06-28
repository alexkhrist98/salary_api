import fastapi
import asyncio

import jwt
import pydantic

import app.models as models
import app.auth as auth
import app.db_logic as db_logic
from main import logger

app = fastapi.FastAPI()

@app.get('/', tags=['ABOUT'])
async def about():
    return {'Message': 'Use /login to gain access to the data'}


@app.get('/login', tags=['LOGIN'], description='This endpoint returns JWT after authentication')
async def login(user_name: str = fastapi.Header(), password: str = fastapi.Header()):
    try:
        password = await auth.hash_password(password)
        employee = await db_logic.fetch_user(models.User(user_name=user_name, password=password))
        if not employee:
            return fastapi.HTTPException(status_code=400, detail='No user with such login')
        elif employee.password != password:
            return fastapi.HTTPException(status_code=400, detail='Invalid password')

        token = await auth.generate_jwt(models.User(user_name=user_name, password=password))
        logger.info('login successful')
        return {'TOKEN': token}
    except pydantic.ValidationError:
        logger.exception('An exception was raised \m %s')
        return fastapi.HTTPException(status_code=500, detail="An error with login function has occured")

@app.get('/salary', tags=['SALARY'])
async def display_salary_and_promotion(token: str = fastapi.Header()):
    try:
        status = await auth.validate(models.Token(token_string=token))
        if status != True:
            return fastapi.HTTPException(status_code=401, detail="Invalid token")
        payload = await auth.token_to_mode(models.Token(token_string=token))
        employee = await db_logic.fetch_user(models.User(user_name=payload.user_name, password=payload.password))
        return {"user_name": employee.user_name, "salary": employee.salary, "promotion_date": employee.promotion_date}
    except pydantic.ValidationError:
        logger.exception()
        return fastapi.HTTPException(status_code=500)

@app.post("/admin", tags=['ADMIN'])
async def create_employee(employee: models.Employee, token: str = fastapi.Header()):
    try:
        await auth.validate(models.Token(token_string=token))
        await auth.check_admin_prev(token)
        employee.password = await auth.hash_password(employee.password)
        await db_logic.create_employee(employee)
        logger.info('Employee create')
        return {"Message": "Employee created succesfully"}
    except Exception:
        logger.exception("An exception has occured")
        return fastapi.HTTPException(status_code=500)
    except fastapi.HTTPException:
        return fastapi.HTTPException(status_code=599)

@app.delete('/admin', tags=["ADMIN"])
async def delete_employee(employee: models.Employee, token: str = fastapi.Header()):
    try:
        await auth.validate(models.Token(token_string=token))
        await auth.check_admin_prev(token)
        await db_logic.delete_employee(employee)
        logger.info('User have been removed')
        return {"Messqge": f"Employee {employee.user_name} was removed"}
    except jwt.ExpiredSignatureError:
        raise fastapi.HTTPException(status_code=403, detail="Your token has expired")
    except fastapi.HTTPException:
        raise fastapi.HTTPException(status_code=403, detail="Access denied")

@app.get('/admin', tags=['ADMIN'])
async def get_employee(user_name: str = fastapi.Header(), token: str = fastapi.Header()):
    try:
        token = models.Token(token_string=token)
        await auth.validate(token)
        await auth.check_admin_prev(token.token_string)
        employee = await db_logic.fetch_user(models.User(user_name=user_name, password=''))
        return employee
    except jwt.ExpiredSignatureError:
        return fastapi.HTTPException(status_code=-402, detail="Your token has expired")
    except fastapi.HTTPException:
        return fastapi.HTTPException(status_code=405, detail='Access denied')

@app.put('/admin', tags=['ADMIN'])
async def update_employee(employee: models.Employee, token: str = fastapi.Header()):
    try:
        token = models.Token(token_string=token)
        await auth.validate(token)
        await auth.check_admin_prev(token.token_string)
        await db_logic.update_employee(employee)
        logger.info("Update is complete")
        return {'Message': f'An employee {employee.user_name} was updated' }
    except jwt.ExpiredSignatureError:
        return fastapi.HTTPException(status_code=402, detail='Your token has expired')
    except fastapi.HTTPException:
        return fastapi.HTTPException(status_code=403, detail="Access denied")