from fastapi import FastAPI
from Routers import attendants, user, appointments
from fastapi.staticfiles import StaticFiles
 

app = FastAPI()

#routers

app.include_router(user.router)
app.include_router(appointments.router)
app.include_router(attendants.router)




@app.get("/")
async def root():
    return "Hola FastAPI"





