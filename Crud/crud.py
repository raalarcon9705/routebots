from sqlalchemy.orm import Session
import Models.models as models, Schemas.schemas as schemas
from Hashing.hashing import Hasher
from sqlalchemy.orm import Session
from Models import models
from Schemas import schemas
from datetime import datetime
from dateutil.parser import parse





def get_user(db: Session, user_id: int = None, email: str = None):
    if user_id is not None:
        return db.query(models.User).filter(models.User.id == user_id).first()
    if email is not None:
        print(f"Searching for email: {email}")
        user = db.query(models.User).filter(models.User.email == email).first()
        print(f"User found: {user}")
        return user



def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = Hasher.bcrypt(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name, username=user.username, super_user=user.super_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_db(db: Session, db_user: models.User, user: schemas.UserUpdate):
    if user.password:
        hashed_password = Hasher.bcrypt(user.password)
        db_user.hashed_password = hashed_password
    if user.email:
        db_user.email = user.email
    if user.full_name:
        db_user.full_name = user.full_name
    if user.super_user is not None:
        db_user.super_user = user.super_user
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_db(db: Session, user: models.User):
    db.delete(user)
    db.commit()


def create_attendant(db: Session, attendant: schemas.AttendantCreate):
    db_attendant = models.Attendant(
        attendant_name=attendant.attendant_name, 
        department=attendant.department, 
        ow=attendant.ow,
        start_time=parse(attendant.start_time).time(),
        end_time=parse(attendant.end_time).time(),
        available_days=attendant.available_days
    )
    db.add(db_attendant)
    db.commit()
    db.refresh(db_attendant)
    return db_attendant






def update_attendant(db: Session, attendant: schemas.AttendantUpdate, attendant_id: int):
    db_attendant = db.query(models.Attendant).filter(models.Attendant.id == attendant_id).first()
    
    if not db_attendant:
        return None

    if attendant.start_time:
        db_attendant.start_time = parse(attendant.start_time).time()
    if attendant.end_time:
        db_attendant.end_time = parse(attendant.end_time).time()
    if attendant.available_days:
        db_attendant.available_days = attendant.available_days

    db.commit()
    db.refresh(db_attendant)
    return db_attendant





#def get_user(db: Session, email: str):
    #return db.query(models.User).filter(models.User.email == email).first()