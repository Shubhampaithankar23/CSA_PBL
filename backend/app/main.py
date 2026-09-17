import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, hash_password, require_admin, verify_password
from .database import Base, engine, get_db
from .models import Student, User
from .schemas import LoginRequest, StudentCreate, StudentResponse, TokenResponse, UserResponse

load_dotenv()
app = FastAPI(title="Secure 3-Tier Web Application", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def seed_database():
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        if not db.scalar(select(User).where(User.username == "admin")):
            db.add_all([
                User(username="admin", email="admin@example.com", password_hash=hash_password("Admin@123"), role="ADMIN"),
                User(username="student", email="student@example.com", password_hash=hash_password("User@123"), role="USER"),
            ])
        if not db.scalar(select(Student)):
            db.add_all([
                Student(student_id="STU-1001", name="Aisha Rahman", email="aisha@example.com", course="Cloud Security", year=2, department="Computing"),
                Student(student_id="STU-1002", name="Daniel Mensah", email="daniel@example.com", course="Network Security", year=3, department="Computing"),
            ])
        db.commit()


@app.on_event("startup")
def startup():
    seed_database()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user}


@app.get("/users/me", response_model=UserResponse)
def read_current_user(user: User = Depends(get_current_user)):
    return user


@app.get("/students", response_model=list[StudentResponse])
def list_students(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Student).order_by(Student.id)).all()


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(payload: StudentCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(Student).where(Student.student_id == payload.student_id)):
        raise HTTPException(status_code=409, detail="Student ID already exists")
    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, payload: StudentCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in payload.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
