from fastapi import FastAPI, HTTPException, Depends, status,APIRouter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import time, timedelta, datetime, date
from dateutil.parser import parse
from Database.database import SessionLocal, engine, Base, get_db
from Schemas.schemas import AppointmentCreate, AppointmentUpdate, User, TokenData
from Models.models import Appointment
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from Token.token_p import SECRET_KEY, ALGORITHM
from jose import JWTError as PyJWTError
from fastapi.security import OAuth2PasswordBearer
from Schemas import schemas
from Crud.crud import get_user as get_user_by_email



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# You might have already imported some of these in your code, so only import the ones you haven't imported yet.



router = APIRouter()



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user







def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def appointment_to_dict(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "customer_name": appointment.customer_name,
        "date_time": appointment.date_time.isoformat(),
        "duration": appointment.duration.isoformat(),
    }

def get_time_slots(duration: timedelta) -> List[time]:
    start_time = time(9, 0)
    end_time = time(17, 0)
    time_slots = []
    current_time = start_time

    while current_time < end_time:
        time_slots.append(current_time)
        current_time = (datetime.combine(date.min, current_time) + duration).time()

    return time_slots

AVAILABLE_TIME_SLOTS = get_time_slots(timedelta(minutes=30))

@router.get("/available-dates")
def get_available_dates(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheduled_appointments = db.query(Appointment.date_time).all()
    scheduled_dates = {appt[0] for appt in scheduled_appointments}
    
    available_dates = []
    for slot in AVAILABLE_TIME_SLOTS:
        current_date = datetime.combine(datetime.today().date(), slot)
        while current_date <= datetime.today() + timedelta(days=30):
            if current_date not in scheduled_dates:
                available_dates.append(current_date.isoformat())
            current_date += timedelta(days=1)

    return available_dates

@router.get("/scheduled-appointments")
def get_scheduled_appointments(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return [appointment_to_dict(appointment) for appointment in appointments]

@router.post("/set-appointment")
def set_available_dates(appointment: AppointmentCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    date_time = parse(appointment.date_time)  # Convert the string to a datetime object

    if date_time.time() not in AVAILABLE_TIME_SLOTS:
        raise HTTPException(status_code=400, detail="Invalid time slot")

    new_appointment = Appointment(
        customer_name=appointment.customer_name,
        date_time=date_time,
        duration=parse(appointment.duration).time(),
            )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return appointment_to_dict(new_appointment)


@router.put("/update-appointment")
def update_appointment(appointment: AppointmentUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).get(appointment.id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    date_time = parse(appointment.date_time)  # Convert the string to a datetime object

    if date_time.time() not in AVAILABLE_TIME_SLOTS:
        raise HTTPException(status_code=400, detail="Invalid time slot")

    db_appointment.customer_name = appointment.customer_name
    db_appointment.date_time = date_time
    db_appointment.duration = parse(appointment.duration).time()

    db.commit()

    return appointment_to_dict(db_appointment)

