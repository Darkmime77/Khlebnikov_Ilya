from sqlalchemy.orm import Session
import models, schemas
def get_user(db: Session, userId: int):
    return db.query(models.Users).filter(models.Users.userId == userId).first()



def get_user_by_login(db: Session, login: str):
    return db.query(models.Users).filter(models.Users.login == login).first()


def get_users(db: Session):
    return db.query(models.Users).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password
    db_user = models.Users(username=user.username, password=fake_hashed_password, isAdmin=user.isAdmin, balance=user.balance, login=user.login)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transport).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Transport(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
