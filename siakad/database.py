"""
SIAKAD - STMIK Amikom Surakarta
Database module: SQLAlchemy models + engine + session.
"""
from __future__ import annotations

import os
from datetime import datetime
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Date, Time,
    DateTime, Float, UniqueConstraint, Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

DB_PATH = os.environ.get("SIAKAD_DB", "siakad.db")
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True,
                      connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(16), nullable=False)  # admin | dosen | mahasiswa
    full_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="user", uselist=False,
                           cascade="all, delete-orphan")
    lecturer = relationship("Lecturer", back_populates="user", uselist=False,
                            cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    nim = Column(String(32), unique=True, nullable=False, index=True)
    program = Column(String(64), nullable=False, default="Teknik Informatika")
    semester = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="student")
    krs = relationship("KRS", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="student",
                               cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="student",
                          cascade="all, delete-orphan")


class Lecturer(Base):
    __tablename__ = "lecturers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    nidn = Column(String(32), unique=True, nullable=False, index=True)
    department = Column(String(64), nullable=False, default="Teknik Informatika")

    user = relationship("User", back_populates="lecturer")
    classes = relationship("Course", back_populates="lecturer")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    code = Column(String(16), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    sks = Column(Integer, nullable=False, default=3)
    semester = Column(Integer, nullable=False, default=1)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id", ondelete="SET NULL"),
                         nullable=True)
    day = Column(String(16), nullable=False, default="Senin")
    time_start = Column(Time, nullable=True)
    time_end = Column(Time, nullable=True)
    room = Column(String(32), nullable=False, default="R.101")

    lecturer = relationship("Lecturer", back_populates="classes")
    krs = relationship("KRS", back_populates="course", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="course",
                               cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="course",
                          cascade="all, delete-orphan")


class KRS(Base):
    __tablename__ = "krs"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_krs"),)
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    academic_year = Column(String(16), nullable=False, default="2025/2026")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="krs")
    course = relationship("Course", back_populates="krs")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "course_id", "date",
                                       name="uq_att"),)
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    status = Column(String(16), nullable=False, default="Hadir")  # Hadir/Izin/Sakit/Alpa
    note = Column(Text, nullable=True)

    student = relationship("Student", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_grade"),)
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    score = Column(Float, nullable=False, default=0.0)
    letter = Column(String(2), nullable=False, default="E")
    academic_year = Column(String(16), nullable=False, default="2025/2026")

    student = relationship("Student", back_populates="grades")
    course = relationship("Course", back_populates="grades")


def score_to_letter(score: float) -> str:
    if score >= 85: return "A"
    if score >= 75: return "B"
    if score >= 65: return "C"
    if score >= 50: return "D"
    return "E"


def letter_to_gp(letter: str) -> float:
    return {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}.get(letter, 0.0)


def init_db() -> None:
    Base.metadata.create_all(ENGINE)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
