from pydantic import BaseModel
from typing import List, Optional
from fastapi import Body
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    id: int
    username: str = Body(..., min_length=3, max_length=30)
    year: int = Body(..., le=2024, ge=1900)
    email: str
    description: str = Body(..., min_length=10, max_length=100)


class TokenData(BaseModel):
    username: Optional[str] = None


class ProductBase(BaseModel):
    name: str
    price: float
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    class Config:
        orm_mode = True


class Product(ProductBase):
    id: int
    department_id: int

    class Config:
        orm_mode = True


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None 


class Department(DepartmentBase):
    id: int
    products: List[Product] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class UserDB(User):
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    year: int
    email: Union[str, None] = None
    description: Union[str, None] = None