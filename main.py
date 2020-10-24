import datetime
import uuid
from typing import List

import databases
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, MetaData, Table, Column, String, CHAR, VARCHAR, Text

# connecting to Postgres Database
DATABASE_URL = "postgresql://test_users:test_passwd@localhost:5433/dbtest"

# connecting to MySQL Database
# DATABASE_URL = "mysql://root:password@localhost:3306/dbtest"

# connecting to sqlite Database
# DATABASE_URL = "sqlite:///test.db"


database = databases.Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", VARCHAR(36), primary_key=True),
    Column("username", Text),
    Column("password", Text),
    Column("first_name", Text),
    Column("last_name", Text),
    Column("gender", Text),
    Column("create_at", Text),
    Column("update_at", Text),
    Column("status", CHAR),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

api = FastAPI(
    title="FastAPI SqlAlchemy CRUD",
    description="This is FastAPI and SqlAlchemy CRUD lab",
    version="1.0.0",
)


@api.on_event("startup")
async def startup():
    await database.connect()


@api.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# create model for List all users
class UserList(BaseModel):
    id: str
    username: str
    password: str
    first_name: str
    last_name: str
    gender: str
    create_at: str
    update_at: str
    status: str


class UserEntry(BaseModel):
    username: str = Field(..., example="johndoe")
    password: str = Field(..., example="yourpassword")
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    gender: str = Field(..., example="M")


class UserUpdate(BaseModel):
    id: str
    first_name: str
    last_name: str
    gender: str
    status: str


# now construct a router
# create route for root
@api.get("/")
async def get_root():
    return {"message": "Welcome to FastAPI SQLAlchemy CRUD test"}


@api.get("/users", response_model=List[UserList])
async def find_all_user():
    query = users.select()
    result = await database.fetch_all(query)
    return result


@api.post("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gID = str(uuid.uuid1())
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        id=gID,
        username=user.username,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        create_at=gDate,
        update_at="",
        status="1",
    )
    await database.execute(query)
    result = {
        "id": gID,
        **user.dict(),
        "create_at": gDate,
        "update_at": "",
        "status": "1",
    }
    return result


@api.get("/users/{user_Id}", response_model=UserList)
async def find_user_by_id(userid: str):
    query = users.select().where(users.c.id == userid)
    return await database.fetch_one(query)


@api.put("/users", response_model=UserList)
async def update_user(user: UserUpdate):
    gDate = str(datetime.datetime.now())
    query = (
        users.update()
        .where(users.c.id == user.id)
        .values(
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            status=user.status,
            update_at=gDate,
        )
    )
    await database.execute(query)
    return await find_user_by_id(user.id)
