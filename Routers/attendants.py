from fastapi import FastAPI, HTTPException, Depends, status,APIRouter
from sqlalchemy.orm import  Session
from typing import List
from datetime import time, timedelta, datetime, date
from Database.database import SessionLocal, engine, Base, get_db
from Models.models import Appointment, Attendant
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from Token.token_p import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from Schemas import schemas
from Crud.crud import get_user, update_attendant
from Crud.crud import create_attendant as create_attendant_crud
from Routers.appointments import get_current_user, get_db
from Routers.appointments import get_current_superuser






oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)




router = APIRouter()




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



@router.post("/attendant", response_model=schemas.Attendant)
def create_attendant(
    attendant: schemas.AttendantCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(
            status_code=400, 
            detail="Current user not properly resolved"
        )

    user = get_user(db, user_id=current_user.id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    db_attendant = create_attendant_crud(db, attendant)

    attendant_response = schemas.Attendant.from_orm(db_attendant)
    return attendant_response



@router.put("/attendant/{attendant_id}", response_model=schemas.Attendant)
def update_route(
    attendant_id: int,
    attendant: schemas.AttendantUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_attendant = update_attendant(db, attendant, attendant_id)
    if db_attendant is None:
        raise HTTPException(status_code=404, detail="Attendant not found")
    return db_attendant


@router.delete("/attendant/{attendant_id}")
def delete_attendant_by_id(
    attendant_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_superuser)
):
    db_attendant = db.query(Attendant).filter(Attendant.id == attendant_id).first()

    if db_attendant is None:
        raise HTTPException(status_code=404, detail="Attendant not found")

    try:
        db.delete(db_attendant)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting attendant") from e

    return {"message": "Attendant deleted successfully"}






