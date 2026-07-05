import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from database import get_session, Student, KRS, Course
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Dashboard Mahasiswa - SIAKAD", layout="wide")
require_role("mahasiswa")
page_header("🏠 Dashboard Mahasiswa", f"Halo, {st.session_state.full_name}.")

DAY_ORDER = {d: i for i, d in enumerate(
    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])}

try:
    with get_session() as s:
        st_row = s.query(Student).filter_by(user_id=st.session_state.user_id).first()
        if not st_row:
            st.warning("Profil mahasiswa belum lengkap."); st.stop()
        krs_rows = (s.query(KRS, Course).join(Course, Course.id == KRS.course_id)
                    .filter(KRS.student_id == st_row.id).all())
        rows = [{
            "Kode": c.code, "Mata Kuliah": c.name, "SKS": c.sks,
            "Hari": c.day,
            "Jam": f"{c.time_start.strftime('%H:%M') if c.time_start else '-'} - "
                   f"{c.time_end.strftime('%H:%M') if c.time_end else '-'}",
            "Ruang": c.room,
            "Dosen": c.lecturer.user.full_name if c.lecturer else "-",
        } for _, c in krs_rows]
        total_sks = sum(r["SKS"] for r in rows)
        info = {"nim": st_row.nim, "program": st_row.program,
                "semester": st_row.semester}
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat data: {e}"); rows = []; total_sks = 0; info = {}

c1, c2, c3 = st.columns(3)
c1.metric("NIM", info.get("nim", "-"))
c2.metric("Semester", info.get("semester", "-"))
c3.metric("Total SKS", total_sks)

st.markdown("### 📅 Jadwal Kuliah Aktif")
df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values(by=["Hari", "Jam"], key=lambda col:
                        col.map(DAY_ORDER) if col.name == "Hari" else col)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
a, b = st.columns(2)
a.page_link("pages/9_Mahasiswa_KRS.py", label="📄 Isi/Ubah KRS")
b.page_link("pages/10_Mahasiswa_KHS.py", label="📊 Lihat KHS")
footer()
