import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
import streamlit as st
import pandas as pd
from database import get_session, Lecturer, Course, KRS, Student, Attendance
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Input Presensi - SIAKAD", layout="wide")
require_role("dosen")
page_header("🗓️ Input Presensi", "Rekam kehadiran mahasiswa per pertemuan.")

STATUS = ["Hadir", "Izin", "Sakit", "Alpa"]

try:
    with get_session() as s:
        lec = s.query(Lecturer).filter_by(user_id=st.session_state.user_id).first()
        if not lec:
            st.warning("Profil dosen belum lengkap."); st.stop()
        classes = s.query(Course).filter_by(lecturer_id=lec.id).all()
        if not classes:
            st.info("Anda belum mengampu kelas."); footer(); st.stop()
        class_map = {c.id: f"{c.code} — {c.name}" for c in classes}
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat kelas: {e}"); st.stop()

c1, c2 = st.columns([2, 1])
course_id = c1.selectbox("Kelas", options=list(class_map.keys()),
                        format_func=lambda i: class_map[i])
tgl = c2.date_input("Tanggal Pertemuan", value=date.today())

try:
    with get_session() as s:
        peserta = (s.query(Student).join(KRS, KRS.student_id == Student.id)
                   .filter(KRS.course_id == course_id).all())
        existing = {a.student_id: a for a in s.query(Attendance)
                    .filter_by(course_id=course_id, date=tgl).all()}
        rows = [{
            "student_id": st_.id, "NIM": st_.nim,
            "Nama": st_.user.full_name,
            "Status": existing[st_.id].status if st_.id in existing else "Hadir",
            "Catatan": existing[st_.id].note or "" if st_.id in existing else "",
        } for st_ in peserta]
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat peserta: {e}"); st.stop()

if not rows:
    st.info("Belum ada peserta pada kelas ini."); footer(); st.stop()

df = pd.DataFrame(rows)
edited = st.data_editor(
    df, hide_index=True, use_container_width=True,
    column_config={
        "student_id": None,
        "NIM": st.column_config.TextColumn(disabled=True),
        "Nama": st.column_config.TextColumn(disabled=True),
        "Status": st.column_config.SelectboxColumn(options=STATUS, required=True),
        "Catatan": st.column_config.TextColumn(),
    },
    key="att_editor",
)

if st.button("💾 Simpan Presensi", type="primary"):
    try:
        with get_session() as s:
            for _, r in edited.iterrows():
                a = (s.query(Attendance)
                     .filter_by(student_id=int(r["student_id"]),
                                course_id=int(course_id), date=tgl).first())
                if a:
                    a.status = r["Status"]; a.note = r["Catatan"] or None
                else:
                    s.add(Attendance(student_id=int(r["student_id"]),
                                     course_id=int(course_id), date=tgl,
                                     status=r["Status"], note=r["Catatan"] or None))
        st.success("Presensi tersimpan.")
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal menyimpan: {e}")

footer()
