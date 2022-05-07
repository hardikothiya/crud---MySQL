import uvicorn
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException


from app import models, schemas, crud
from app.database import engine, SessionLocal

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


@app.post("/user", response_model=schemas.UserInfo, tags=['User'])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/username/{user_name}", tags=['User'])
def show_username(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user_name)

    return {"name": db_user[0].username,
            "fullname": db_user[0].fullname,
            "id": db_user[0].id
            }


@app.get("/all", tags=['User'])
def show_username(db: Session = Depends(get_db)):
    db_user = crud.all_user(db)
    return db_user


@app.delete("/user/{user_name}", tags=['User'])
def delete_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, username=user_name)
    return {"User deleted successfully!! "}


@app.post("/user/", tags=['User'])
def update_user(user_name: str, full_name: str, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, username=user_name, full_name=full_name)
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3306)
