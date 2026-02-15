import os

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal
from auth import create_token, verify_token
from config import ADMIN_USERNAME, ADMIN_PASSWORD


# ===============================
# CREATE DATABASE TABLES
# ===============================

models.Base.metadata.create_all(bind=engine)


# ===============================
# CREATE FASTAPI APP
# ===============================

app = FastAPI(title="M-MATH")


# ===============================
# CREATE UPLOAD DIRECTORY
# ===============================

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===============================
# STATIC AND TEMPLATE SETUP
# ===============================

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")


# ===============================
# DATABASE DEPENDENCY
# ===============================

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ===============================
# HOME PAGE
# ===============================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ===============================
# SIGNUP (STUDENT)
# ===============================

@app.post("/signup")
def signup(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing:

        return RedirectResponse("/", status_code=302)


    new_user = models.User(
        username=username,
        password=password,
        role="student"
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/", status_code=302)


# ===============================
# LOGIN
# ===============================

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # ADMIN LOGIN
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

        token = create_token({
            "username": username,
            "role": "admin"
        })

        response = RedirectResponse("/admin", status_code=302)

        response.set_cookie(
            key="token",
            value=token,
            httponly=True
        )

        return response


    # STUDENT LOGIN
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.password == password
    ).first()

    if user:

        token = create_token({
            "username": username,
            "role": "student"
        })

        response = RedirectResponse("/student", status_code=302)

        response.set_cookie(
            key="token",
            value=token,
            httponly=True
        )

        return response


    return RedirectResponse("/", status_code=302)


# ===============================
# ADMIN DASHBOARD
# ===============================

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not token:

        return RedirectResponse("/", status_code=302)

    try:

        data = verify_token(token)

    except:

        return RedirectResponse("/", status_code=302)


    if data["role"] != "admin":

        return RedirectResponse("/", status_code=302)


    files = db.query(models.File).all()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "files": files,
            "username": data["username"]
        }
    )


# ===============================
# STUDENT DASHBOARD
# ===============================

@app.get("/student", response_class=HTMLResponse)
def student_dashboard(
    request: Request,
    token: str = Cookie(None)
):

    if not token:

        return RedirectResponse("/", status_code=302)

    try:

        data = verify_token(token)

    except:

        return RedirectResponse("/", status_code=302)


    if data["role"] != "student":

        return RedirectResponse("/", status_code=302)


    return templates.TemplateResponse(
        "student.html",
        {
            "request": request,
            "username": data["username"]
        }
    )


# ===============================
# GET FILES BY CLASS (STUDENT)
# ===============================

@app.get("/files/{class_name}")
def get_files(
    class_name: str,
    token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not token:

        return JSONResponse([])

    try:

        verify_token(token)

    except:

        return JSONResponse([])


    files = db.query(models.File).filter(
        models.File.class_name == class_name
    ).all()


    return [

        {
            "id": f.id,
            "class_name": f.class_name,
            "topic": f.topic,
            "filename": f.filename,
            "uploaded_by": f.uploaded_by
        }

        for f in files

    ]


# ===============================
# FILE UPLOAD (ADMIN ONLY)
# ===============================

@app.post("/upload")
def upload_file(
    class_name: str = Form(...),
    topic: str = Form(...),
    file: UploadFile = File(...),
    token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not token:

        return RedirectResponse("/", status_code=302)

    data = verify_token(token)

    if data["role"] != "admin":

        return RedirectResponse("/", status_code=302)


    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:

        buffer.write(file.file.read())


    new_file = models.File(

        class_name=class_name,
        topic=topic,
        filename=file.filename,
        uploaded_by=data["username"]

    )

    db.add(new_file)
    db.commit()

    return RedirectResponse("/admin", status_code=302)


# ===============================
# DELETE FILE (ADMIN ONLY)
# ===============================

@app.get("/delete/{file_id}")
def delete_file(
    file_id: int,
    token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not token:

        return RedirectResponse("/", status_code=302)

    data = verify_token(token)

    if data["role"] != "admin":

        return RedirectResponse("/", status_code=302)


    file = db.query(models.File).filter(
        models.File.id == file_id
    ).first()

    if file:

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        if os.path.exists(file_path):

            os.remove(file_path)

        db.delete(file)
        db.commit()


    return RedirectResponse("/admin", status_code=302)


# ===============================
# LOGOUT
# ===============================

@app.get("/logout")
def logout():

    response = RedirectResponse("/", status_code=302)

    response.delete_cookie("token")

    return response
