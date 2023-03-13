from pydantic import BaseModel, validator


# import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    password_confirmation: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     # created_at: datetime

#     class Config:
#         orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool


# TODO add schemes everywhere
