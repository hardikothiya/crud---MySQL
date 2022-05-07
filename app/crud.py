from sqlalchemy.orm import Session

from . import models, schemas


# def get_user_by_username(db: Session, username: str):
#     db_user = db.query(models.UserInfo).filter(models.UserInfo.username == username).all()
#     return db_user

def get_user_by_username(db: Session, username: str):
    db_user = db.query(models.UserInfo).filter(models.UserInfo.username == username).all()
    return db_user


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password
    db_user = models.UserInfo(username=user.username, password=fake_hashed_password, fullname=user.fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def all_user(db: Session):
    return db.query(models.UserInfo).all()


def delete_user(db: Session, username: str):
    db_user = db.query(models.UserInfo).filter(models.UserInfo.username == username).first()
    db.delete(db_user)
    db.commit()
    return db_user


def update_user(db: Session, username: str, full_name: str):
    db_user = db.query(models.UserInfo).filter(models.UserInfo.username == username).first()
    db_user.fullname = full_name
    db.commit()
    db.refresh(db_user)
    return db_user
