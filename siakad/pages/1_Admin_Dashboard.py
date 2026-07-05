import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from sqlalchemy import func
from database import get_session, User, Student, Lecturer, Course, KRS, Grade
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Admin Dashboard - SIAKAD", layout="wide")
require_role("admin")
page_header("🛠️ Admin Dashboard", "Ringkasan sistem akademik.")

try:
    with get_session() as s:
        n_users    = s.query(func.count(User.id)).scalar() or 0
        n_students = s.query(func.count(Student.id)).scalar() or 0
        n_lect     = s.query(func.count(Lecturer.id)).scalar() or 0
        n_courses  = s.query(func.count(Course.id)).scalar() or 0
        n_krs      = s.query(func.count(KRS.id)).scalar() or 0
        n_grades   = s.query(func.count(Grade.id)).scalar() or 0
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat statistik: {e}")
    n_users = n_students = n_lect = n_courses = n_krs = n_grades = 0

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="kpi" style="background:linear-gradient(135deg,#0046FF,#0033B8);color:white;padding:1rem;border-radius:12px;"><p>Mahasiswa</p><h2 style="color:white;margin:0">{n_students}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi" style="background:linear-gradient(135deg,#0046FF,#0033B8);color:white;padding:1rem;border-radius:12px;"><p>Dosen</p><h2 style="color:white;margin:0">{n_lect}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi" style="background:linear-gradient(135deg,#0046FF,#0033B8);color:white;padding:1rem;border-radius:12px;"><p>Mata Kuliah</p><h2 style="color:white;margin:0">{n_courses}</h2></div>', unsafe_allow_html=True)

st.markdown(" ")
c4, c5, c6 = st.columns(3)
c4.metric("Total User", n_users)
c5.metric("Entri KRS", n_krs)
c6.metric("Entri Nilai", n_grades)

st.markdown("---")
st.markdown("### Modul Cepat")
a, b, c = st.columns(3)
a.page_link("pages/2_Manage_Students.py", label="👨‍🎓 Kelola Mahasiswa")
b.page_link("pages/3_Manage_Lecturers.py", label="👩‍🏫 Kelola Dosen")
c.page_link("pages/4_Manage_Courses.py", label="📘 Kelola Mata Kuliah")

footer()
