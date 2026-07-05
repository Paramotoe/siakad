import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from database import get_session, Lecturer, Course, KRS
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Dashboard Dosen - SIAKAD", layout="wide")
require_role("dosen")
page_header("📚 Dashboard Dosen", f"Selamat datang, {st.session_state.full_name}.")

try:
    with get_session() as s:
        lec = s.query(Lecturer).filter_by(user_id=st.session_state.user_id).first()
        if not lec:
            st.warning("Profil dosen belum lengkap."); st.stop()
        classes = s.query(Course).filter_by(lecturer_id=lec.id).all()
        rows = []
        total_students = 0
        for c in classes:
            n = s.query(KRS).filter_by(course_id=c.id).count()
            total_students += n
            rows.append({
                "Kode": c.code, "Mata Kuliah": c.name, "SKS": c.sks,
                "Hari": c.day,
                "Jam": f"{c.time_start.strftime('%H:%M') if c.time_start else '-'} - "
                       f"{c.time_end.strftime('%H:%M') if c.time_end else '-'}",
                "Ruang": c.room, "Peserta": n,
            })
        df = pd.DataFrame(rows)
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat data: {e}")
    df = pd.DataFrame(); total_students = 0

c1, c2, c3 = st.columns(3)
c1.metric("Kelas Diampu", len(df))
c2.metric("Total Peserta", total_students)
c3.metric("NIDN", lec.nidn if 'lec' in locals() and lec else "-")

st.markdown("### Kelas yang Diampu")
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
a, b = st.columns(2)
a.page_link("pages/6_Dosen_Attendance.py", label="🗓️ Input Presensi")
b.page_link("pages/7_Dosen_Grades.py", label="📝 Input Nilai")
footer()
