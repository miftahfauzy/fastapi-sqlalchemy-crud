import datetime
import uuid
from typing import List

import databases
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, MetaData, Table, Column, String, CHAR

# coneecting to Postgres Database
DATABASE_URL = "postgresql://test_users:test_passwd@localhost:5432/dbtest"
database = databases.Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("username", String),
    Column("password", String),
    Column("first_name", String),
    Column("last_name", String),
    Column("gender", String),
    Column("create_at", String),
    Column("update_at", String),
    Column("status", CHAR)
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

api = FastAPI(
    title="FastAPI SqlAchemy CRUD",
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


# now construct a router
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
        status="1"
    )
    await database.execute(query)
    result = {
        "id": gID,
        **user.dict(),
        "create_at": gDate,
        "update_at": "",
        "status": "1"
    }
    return result
