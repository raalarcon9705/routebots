from sqlalchemy.orm import Session
import Models.models as models, Schemas.schemas as schemas
from Hashing.hashing import Hasher
from sqlalchemy.orm import Session
from Models import models
from Schemas import schemas

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
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name, username=user.username)
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
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_db(db: Session, user: models.User):
    db.delete(user)
    db.commit()


def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()