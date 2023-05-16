# schemas.py
from typing import List, Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    super_user: int = 0 

class UserUpdate(UserBase):
    password: Optional[str] = None
    super_user: Optional[int] = None 

class User(UserBase):
    id: int
    disabled: Optional[bool] = None
    super_user: int

    class Config:
        orm_mode = True


class AppointmentCreate(BaseModel):
    customer_name: str
    date_time: str
    duration: str
    attendant_id: int

class AppointmentUpdate(BaseModel):
    id: int
    customer_name: str
    date_time: str
    duration: str

class TokenData(BaseModel):
    email: Optional[str] = None



class AttendantBase(BaseModel):
    id: int
    attendant_name: str
    department: str
    ow: int


class AttendantCreate(BaseModel):
    attendant_name: str
    department: str
    ow: int
    start_time: str
    end_time: str
    available_days: str   # A string of comma-separated days, e.g., "Monday,Tuesday,Wednesday"

    class Config:
        orm_mode = True


   

class Attendant(AttendantBase):
    id: int
    attendant_name: str
    department: str
    ow: int

    class Config:
        orm_mode = True



class AttendantUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    available_days: Optional[str] = None





