from pydantic import BaseModel, validator


# import datetime

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    password_confirmation: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     # created_at: datetime

#     class Config:
#         orm_mode = True

class UserLogin(UserBase):
    password: str

# TODO response user scheme, 
# TODO add schemes everywhere