from typing import List

import databases
from fastapi import FastAPI
from pydantic import BaseModel
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

api = FastAPI()


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


# now construct a router
@api.get("/users", response_model=List[UserList])
async def find_all_user():
    query = users.select()
    result = await database.fetch_all(query)
    return result
