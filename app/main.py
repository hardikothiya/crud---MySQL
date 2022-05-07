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


@app.post("/user", response_model=schemas.UserInfo)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/username/{user_name}")
def show_username(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user_name)
    return db_user


@app.delete("/user/{user_name}")
def delete_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, username=user_name)
    return {"User deleted" }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3306)
