from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt

SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return product # ._.
    return None

def delete_department(db: Session, department_id: int):
    department_to_delete = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department_to_delete:
        return None
    db.delete(department_to_delete)
    db.commit()
    return department_to_delete

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserBase):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = models.User(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_department(db: Session, department_id: int):
    return db.query(models.Department).filter(models.Department.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(name=department.name, description=department.description)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_department_product(db: Session, product: schemas.ProductCreate, department_id: int):
    db_product = models.Product(name=product.name,
                                price=product.price,
                                department_id=department_id,
                                image_url=product.image_url
                                )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product