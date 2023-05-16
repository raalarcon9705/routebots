from sqlalchemy import Boolean, Column, Integer, String
from Database.database import Base
from pydantic import BaseModel
from datetime import time, timedelta, datetime, date
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Time, func
from sqlalchemy import ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(50))
    username = Column(String(50))
    disabled = Column(Boolean, default=False)
    super_user = Column(Integer, default=0)  



class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(50), index=True)
    date_time = Column(DateTime, index=True)
    duration = Column(Time, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    attendant_id = Column(Integer, ForeignKey("attendants.id"))



class Attendant(Base):
    __tablename__ = "attendants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attendant_name = Column(String(50), index=True)
    department = Column(String(50), index=True)
    ow = Column(Integer, ForeignKey("users.id"))
    start_time = Column(Time)
    end_time = Column(Time)
    available_days = Column(String(1000))  # We can store the available days as a comma-separated string


