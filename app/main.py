import time

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pymemcache.client import base

import json
from . import models, schemas, crud
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
def take_lock():
    global db
    db = SessionLocal()


@app.post("/user", response_model=schemas.UserInfo, tags=['User'])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/user/id", tags=['User'])
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    client = base.Client(('127.0.0.1', 11211))

    db_user = client.get(str(user_id))
    if db_user is not None:
        print("===========cached data=========")
        s = db_user.decode("utf-8").replace("'", '"')
        z = "[" + s + "]"
        db_user = json.loads(z)
        return db_user

    if db_user is None:
        print("===========Query from server=========")
        db_user = crud.get_user_by_id(db, user_id=user_id)

        try:
            client.set(str(db_user.id), {"username": db_user.username,
                                         "fullname": db_user.fullname,
                                         "id": db_user.id}, expire=86400)
            print(client.set(str(db_user.id), {"username": db_user.username,
                                               "fullname": db_user.fullname,
                                               "id": db_user.id}, expire=86400))
            db_user = client.get(str(user_id))
            if db_user is not None:
                s = db_user.decode("utf-8").replace("'", '"')
                z = "[" + s + "]"
                db_user = json.loads(z)
            return db_user
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="User not found")

    return db_user


# ############################################################################################################################

@app.get("/username/{user_name}", tags=['User'])
def show_username(user_name: str, db: Session = Depends(get_db)):
    client = base.Client(('127.0.0.1', 11211))
    print("===========cached data=========")
    db_user = client.get(user_name)
    if db_user is not None:
        s = db_user.decode("utf-8").replace("'", '"')
        z = "[" + s + "]"
        db_user = json.loads(z)

    if db_user is None:
        print("===========Query from server=========")
        db_user = crud.get_user_by_username(db, username=user_name)
        try:
            client.set(db_user[0].username, {"username": db_user[0].username,
                                             "fullname": db_user[0].fullname,
                                             "id": db_user[0].id}, expire=86400)
            db_user = client.get(user_name)
            if db_user is not None:
                s = db_user.decode("utf-8").replace("'", '"')
                z = "[" + s + "]"
                db_user = json.loads(z)
            return db_user

        except Exception as e:
            print(e)
            return str(e)

    return db_user


##############################################################################################


########################################################################################################################

@app.get("/all", tags=['User'])
def show_username(db: Session = Depends(get_db)):
    db_user = crud.all_user(db)
    return db_user


@app.delete("/user/{user_name}", tags=['User'])
def delete_user(user_name: str, db: Session = Depends(get_db)):
    client = base.Client(('127.0.0.1', 11211))
    client.delete(user_name)
    db_user = crud.delete_user(db, username=user_name)
    client.delete(str(db_user.id))

    return {"User deleted successfully!! "}


@app.post("/user/", tags=['User'])
def update_user(user_name: str, full_name: str, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, username=user_name, full_name=full_name)
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
