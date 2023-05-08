from sqlalchemy import Boolean, Column, Integer, String
from Database.database import Base
from pydantic import BaseModel
from datetime import time, timedelta, datetime, date
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Time, func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(50))
    username = Column(String(50))
    disabled = Column(Boolean, default=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    date_time = Column(DateTime, index=True)
    duration = Column(Time, index=True)