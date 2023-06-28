import pydantic

class User(pydantic.BaseModel):
    user_name: str = None
    password: str = None

class Employee(pydantic.BaseModel):
    user_name: str = None
    password: str = None
    salary: float = None
    promotion_date: str = None

class Token_payload(pydantic.BaseModel):
    user_name: str
    password: str
    exp: int

class Token(pydantic.BaseModel):
    token_string: str