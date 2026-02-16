import os

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Class, Subject, Chapter, Note
from config import ADMIN_SECRET


Base.metadata.create_all(bind=engine)

app = FastAPI(title="M MATH")


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================
# LANDING
# ==========================

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):

    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )


# ==========================
# ADMIN ACCESS
# ==========================

@app.post("/admin-access")
def admin_access(secret: str = Form(...)):

    if secret == ADMIN_SECRET:

        return RedirectResponse("/admin", status_code=302)

    return RedirectResponse("/", status_code=302)


# ==========================
# ADMIN PAGE
# ==========================

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):

    classes = db.query(Class).all()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "classes": classes
        }
    )


# ==========================
# STUDENT PAGE
# ==========================

@app.get("/student", response_class=HTMLResponse)
def student_page(request: Request, db: Session = Depends(get_db)):

    classes = db.query(Class).all()

    return templates.TemplateResponse(
        "student.html",
        {
            "request": request,
            "classes": classes
        }
    )


# ==========================
# CREATE CLASS
# ==========================

@app.post("/create-class")
def create_class(name: str = Form(...), db: Session = Depends(get_db)):

    db.add(Class(name=name))

    db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# DELETE CLASS
# ==========================

@app.get("/delete-class/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):

    class_obj = db.query(Class).filter(
        Class.id == class_id
    ).first()

    if class_obj:

        # delete notes files
        for subject in class_obj.subjects:
            for chapter in subject.chapters:
                for note in chapter.notes:

                    path = os.path.join(UPLOAD_DIR, note.filename)

                    if os.path.exists(path):
                        os.remove(path)

        db.delete(class_obj)

        db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# CREATE SUBJECT
# ==========================

@app.post("/create-subject")
def create_subject(
    name: str = Form(...),
    class_id: int = Form(...),
    db: Session = Depends(get_db)
):

    db.add(
        Subject(
            name=name,
            class_id=class_id
        )
    )

    db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# DELETE SUBJECT
# ==========================

@app.get("/delete-subject/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):

    subject = db.query(Subject).filter(
        Subject.id == subject_id
    ).first()

    if subject:

        for chapter in subject.chapters:
            for note in chapter.notes:

                path = os.path.join(UPLOAD_DIR, note.filename)

                if os.path.exists(path):
                    os.remove(path)

        db.delete(subject)

        db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# CREATE CHAPTER
# ==========================

@app.post("/create-chapter")
def create_chapter(
    name: str = Form(...),
    subject_id: int = Form(...),
    db: Session = Depends(get_db)
):

    db.add(
        Chapter(
            name=name,
            subject_id=subject_id
        )
    )

    db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# DELETE CHAPTER
# ==========================

@app.get("/delete-chapter/{chapter_id}")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):

    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id
    ).first()

    if chapter:

        for note in chapter.notes:

            path = os.path.join(UPLOAD_DIR, note.filename)

            if os.path.exists(path):
                os.remove(path)

        db.delete(chapter)

        db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# UPLOAD NOTE
# ==========================

@app.post("/upload-note")
def upload_note(
    title: str = Form(...),
    chapter_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    db.add(
        Note(
            title=title,
            filename=file.filename,
            chapter_id=chapter_id
        )
    )

    db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# DELETE NOTE
# ==========================

@app.get("/delete-note/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):

    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if note:

        path = os.path.join(UPLOAD_DIR, note.filename)

        if os.path.exists(path):
            os.remove(path)

        db.delete(note)

        db.commit()

    return RedirectResponse("/admin", status_code=302)


# ==========================
# API ENDPOINTS
# ==========================

@app.get("/api/subjects/{class_id}")
def get_subjects(class_id: int, db: Session = Depends(get_db)):

    subjects = db.query(Subject).filter(
        Subject.class_id == class_id
    ).all()

    return [
        {"id": s.id, "name": s.name}
        for s in subjects
    ]


@app.get("/api/chapters/{subject_id}")
def get_chapters(subject_id: int, db: Session = Depends(get_db)):

    chapters = db.query(Chapter).filter(
        Chapter.subject_id == subject_id
    ).all()

    return [
        {"id": c.id, "name": c.name}
        for c in chapters
    ]


@app.get("/api/notes/{chapter_id}")
def get_notes(chapter_id: int, db: Session = Depends(get_db)):

    notes = db.query(Note).filter(
        Note.chapter_id == chapter_id
    ).all()

    return [
        {"title": n.title, "filename": n.filename}
        for n in notes
    ]


# ==========================
# VIEW FILE
# ==========================

@app.get("/view/{filename}")
def view_file(filename: str):

    path = os.path.join(UPLOAD_DIR, filename)

    return FileResponse(path, media_type="application/pdf")


# ==========================
# DOWNLOAD FILE
# ==========================

@app.get("/download/{filename}")
def download_file(filename: str):

    path = os.path.join(UPLOAD_DIR, filename)

    return FileResponse(path, filename=filename)
