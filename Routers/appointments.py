from fastapi import FastAPI, HTTPException, Depends, status,APIRouter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import time, timedelta, datetime, date
from dateutil.parser import parse
from Database.database import SessionLocal, engine, Base, get_db
from Schemas.schemas import AppointmentCreate, AppointmentUpdate, User, TokenData
from Models.models import Appointment, Attendant, User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from Token.token_p import SECRET_KEY, ALGORITHM
from jose import JWTError as PyJWTError
from fastapi.security import OAuth2PasswordBearer
from Schemas import schemas
from Crud.crud import get_user as get_user_by_email
from sqlalchemy import and_




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



def get_current_superuser(current_user: schemas.User = Depends(get_current_user)):
    if current_user.super_user != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user





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





@router.get("/available-dates/{attendant_id}")
def get_available_dates(attendant_id: int, db: Session = Depends(get_db)):
    # Fetch attendant details
    attendant = db.query(Attendant).filter(Attendant.id == attendant_id).first()
    
    if not attendant:
        raise HTTPException(status_code=404, detail="Attendant not found")
    
    # Parse available_days into a set of integers
    available_days = set(map(int, attendant.available_days.split(',')))
    
    # Fetch existing appointments for the attendant
    existing_appointments = db.query(Appointment.date_time).filter(Appointment.attendant_id == attendant_id).all()
    existing_dates = {appt[0] for appt in existing_appointments}

    available_dates = []
    start_time = datetime.combine(datetime.today(), attendant.start_time)
    end_time = datetime.combine(datetime.today(), attendant.end_time)
    current_date = start_time

    # Check the availability for the next 30 days
    while current_date <= datetime.today() + timedelta(days=30):
        # Check if the current day of the week is available and the time slot is not booked
        if current_date.weekday() in available_days and current_date not in existing_dates:
            # Check if the current date is within the attendant's working hours
            if start_time.time() <= current_date.time() <= end_time.time():
                available_dates.append(current_date.isoformat())
        current_date += timedelta(minutes=30)  # Assume the minimum appointment duration is 30 minutes

    return available_dates


@router.post("/set-appointment")
def set_appointments(appointment: AppointmentCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    date_time = parse(appointment.date_time)  # Convert the string to a datetime object

    if date_time.time() not in AVAILABLE_TIME_SLOTS:
        raise HTTPException(status_code=400, detail="Invalid time slot")

    # Check if there is an existing appointment at the same time with the same attendant
    existing_appointment = db.query(Appointment).filter(and_(Appointment.date_time == date_time, Appointment.attendant_id == appointment.attendant_id)).first()
    
    if existing_appointment is not None:
        raise HTTPException(status_code=400, detail="The time slot is not available. Please select another time slot or another attendant.")

    new_appointment = Appointment(
        customer_name=appointment.customer_name,
        date_time=date_time,
        duration=parse(appointment.duration).time(),
        user_id=current_user.id,  # Assign the ID of the current user to the new appointment
        attendant_id=appointment.attendant_id,  # Assign the ID of the attendant to the new appointment
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return appointment_to_dict(new_appointment)



#Pedir los appointments ingresando el attendant_id.
@router.get("/scheduled-appointments/{attendant_id}")
def get_scheduled_appointments_by_attendant(attendant_id: int, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).filter(Appointment.attendant_id == attendant_id).all()
    return [appointment_to_dict(appointment) for appointment in appointments]



#Pedir los appointments ingresando el user_id.
@router.get("/scheduled-appointments-user/{user_id}")
def get_scheduled_appointments_by_user_id(user_id: int, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).filter(Appointment.user_id == user_id).all()
    return [appointment_to_dict(appointment) for appointment in appointments]






@router.put("/update-appointment")
def update_appointment(appointment: AppointmentUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).get(appointment.id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.super_user == 0 and db_appointment.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    date_time = parse(appointment.date_time)  # Convert the string to a datetime object

    if date_time.time() not in AVAILABLE_TIME_SLOTS:
        raise HTTPException(status_code=400, detail="Invalid time slot")

    db_appointment.customer_name = appointment.customer_name
    db_appointment.date_time = date_time
    db_appointment.duration = parse(appointment.duration).time()

    db.commit()

    return appointment_to_dict(db_appointment)


#Eliminar appointments
@router.delete("/delete-appointment/{appointment_id}")
def delete_appointment(appointment_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).get(appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.super_user == 0 and db_appointment.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(db_appointment)  # Especificar el objeto a eliminar
    db.commit()
