from fastapi import APIRouter, HTTPException, FastAPI, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from Database.database import SessionLocal, engine,get_db
from Crud.crud import get_user, get_users, create_user, update_user_db, delete_user_db
from Hashing.hashing import Hasher
from Token.token_p import create_access_token
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import Models.models as models
import Schemas.schemas as schemas
from Routers.appointments import get_current_user, get_current_superuser



router = APIRouter()

models.Base.metadata.create_all(bind=engine)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def authenticate_user(db: Session, email: str, password: str): 
    user = get_user(db, email=email)
    print(f"User: {user}")
    if not user:
        return False
    password_verification = Hasher.verify(user.hashed_password, password)
    print(f"Password verification: {password_verification}")
    if not password_verification:
        return False
    return user




@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Email: {form_data.username}, Password: {form_data.password}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_superuser)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_superuser)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



@router.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_superuser)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user_db(db=db, db_user=db_user, user=user)


@router.delete("/users/{user_id}")
def delete_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_superuser)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user_db(db=db, user=db_user)
    return {"message": "User deleted"}



