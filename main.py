from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging
import bcrypt
from db import crud, models, schemas
from db.database import SessionLocal, engine
from typing import List
from typing import Optional

app = FastAPI()

templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Користувач вже існує!"})
    crud.create_user(db, schemas.UserBase(username=username, password=password))
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Невірний логін або пароль!"})
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/departments", response_class=HTMLResponse)
async def department_page(request: Request, db: Session = Depends(get_db)):
    departments = crud.get_departments(db)
    return templates.TemplateResponse("departments.html", {"request": request, "departments": departments})

@app.post("/dashboard/departments", response_class=HTMLResponse)
async def create_department_page(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    crud.create_department(db, schemas.DepartmentCreate(name=name, description=description))
    return RedirectResponse("/dashboard/departments", status_code=302)

@app.post("/dashboard/departments/delete/{department_id}", response_class=HTMLResponse)
async def delete_department_page(department_id: int, db: Session = Depends(get_db)):
    deleted_department = crud.delete_department(db, department_id)
    if not deleted_department:
        raise HTTPException(status_code=404, detail="Department not found!")
    return RedirectResponse("/dashboard/departments", status_code=302)

@app.get("/dashboard/products", response_class=HTMLResponse)
async def product_page(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    departments = crud.get_departments(db)
    return templates.TemplateResponse("products.html", {"request": request, "products": products, "departments": departments})

@app.post("/dashboard/products", response_class=HTMLResponse)
async def create_product_page(request: Request,
                                name: str = Form(...),
                                price: float = Form(...),
                                department_id: int = Form(...),
                                image_url: Optional[str] = Form(None),
                                db: Session = Depends(get_db)
                                ):
    crud.create_department_product(
        db, schemas.ProductCreate(name=name, price=price, image_url=image_url), department_id
    )
    return RedirectResponse("/dashboard/products", status_code=302)

@app.post("/dashboard/products/delete/{product_id}", response_class=HTMLResponse)
async def delete_product_page(product_id: int, db: Session = Depends(get_db)):
    deleted_product = crud.delete_product(db, product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено!")
    return RedirectResponse("/dashboard/products", status_code=302)

@app.post("/dashboard/products/delete-selected", response_class=HTMLResponse)
async def delete_selected_products(product_ids: List[int] = Form(...), db: Session = Depends(get_db)):
    for product_id in product_ids:
        crud.delete_product(db, product_id)
    return RedirectResponse("/dashboard/products", status_code=302)

@app.get("/dashboard/products/view", response_class=HTMLResponse)
async def view_products(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    departments = crud.get_departments(db)

    return templates.TemplateResponse("products_view.html", {
        "request": request,
        "products": products,
        "departments": departments
    })

@app.get("/dashboard/departments/view", response_class=HTMLResponse)
async def view_departments(request: Request, db: Session = Depends(get_db)):
    departments = crud.get_departments(db)

    return templates.TemplateResponse("departments_view.html", {
        "request": request,
        "departments": departments
    })

if __name__ == "__main__":
    import os
    os.system("uvicorn main:app --reload")