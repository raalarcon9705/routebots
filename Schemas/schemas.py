from typing import List, Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True


class AppointmentCreate(BaseModel):
    customer_name: str
    date_time: str
    duration: str

class AppointmentUpdate(BaseModel):
    id: int
    customer_name: str
    date_time: str
    duration: str

class TokenData(BaseModel):
    email: Optional[str] = None