"""Seeder for SIAKAD demo data."""
from __future__ import annotations

from datetime import time, date, timedelta
import bcrypt

from database import (
    init_db, get_session, User, Student, Lecturer, Course, KRS,
    Attendance, Grade, score_to_letter,
)


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def seed() -> None:
    init_db()
    with get_session() as s:
        if s.query(User).count() > 0:
            print("Already seeded.")
            return

        # --- Admin ---
        admin = User(username="admin", password_hash=hash_pw("admin123"),
                     role="admin", full_name="Administrator SIAKAD")
        s.add(admin)

        # --- Lecturers ---
        lect_data = [
            ("dosen1", "Dr. Budi Santoso, M.Kom.", "0601018001"),
            ("dosen2", "Siti Aminah, M.T.",        "0602028002"),
            ("dosen3", "Agus Prakoso, M.Cs.",      "0603038003"),
        ]
        lecturers: list[Lecturer] = []
        for uname, name, nidn in lect_data:
            u = User(username=uname, password_hash=hash_pw("dosen123"),
                     role="dosen", full_name=name)
            l = Lecturer(user=u, nidn=nidn, department="Teknik Informatika")
            s.add(u); s.add(l)
            lecturers.append(l)
        s.flush()

        # --- Courses ---
        course_data = [
            ("IF101", "Algoritma & Pemrograman", 3, 1, lecturers[0], "Senin",  time(8, 0),  time(10, 30), "R.101"),
            ("IF102", "Basis Data",              3, 3, lecturers[1], "Selasa", time(10, 0), time(12, 30), "R.202"),
            ("IF103", "Rekayasa Perangkat Lunak",3, 5, lecturers[2], "Rabu",   time(13, 0), time(15, 30), "R.303"),
            ("IF104", "Kecerdasan Buatan",       3, 5, lecturers[0], "Kamis",  time(8, 0),  time(10, 30), "R.104"),
            ("IF105", "Jaringan Komputer",       3, 3, lecturers[1], "Jumat",  time(10, 0), time(12, 30), "R.205"),
            ("IF106", "Sistem Operasi",          3, 3, lecturers[2], "Senin",  time(13, 0), time(15, 30), "R.106"),
        ]
        courses: list[Course] = []
        for code, name, sks, sem, lect, day, t1, t2, room in course_data:
            c = Course(code=code, name=name, sks=sks, semester=sem,
                       lecturer=lect, day=day, time_start=t1, time_end=t2, room=room)
            s.add(c); courses.append(c)
        s.flush()

        # --- Students ---
        stud_data = [
            ("mahasiswa1", "Andi Wijaya",   "22.11.0001", 3),
            ("mahasiswa2", "Rina Kartika",  "22.11.0002", 3),
            ("mahasiswa3", "Dedi Kurniawan","22.11.0003", 5),
            ("mahasiswa4", "Sari Melati",   "22.11.0004", 5),
            ("mahasiswa5", "Fajar Hidayat", "23.11.0005", 1),
        ]
        students: list[Student] = []
        for uname, name, nim, sem in stud_data:
            u = User(username=uname, password_hash=hash_pw("mhs123"),
                     role="mahasiswa", full_name=name)
            st = Student(user=u, nim=nim, program="Teknik Informatika", semester=sem)
            s.add(u); s.add(st)
            students.append(st)
        s.flush()

        # --- KRS: enroll each student to courses matching their semester ---
        for st in students:
            for c in courses:
                if c.semester <= st.semester:
                    s.add(KRS(student_id=st.id, course_id=c.id))
        s.flush()

        # --- Attendance (last 3 weeks, sample) ---
        today = date.today()
        for st in students:
            for c in courses:
                if c.semester > st.semester:
                    continue
                for w in range(3):
                    d = today - timedelta(days=7 * w)
                    s.add(Attendance(student_id=st.id, course_id=c.id,
                                     date=d, status="Hadir"))

        # --- Grades (deterministic sample) ---
        import random
        random.seed(42)
        for st in students:
            for c in courses:
                if c.semester > st.semester:
                    continue
                score = round(random.uniform(60, 95), 1)
                s.add(Grade(student_id=st.id, course_id=c.id,
                            score=score, letter=score_to_letter(score)))
        print("Seed done.")


if __name__ == "__main__":
    seed()
