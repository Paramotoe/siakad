import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from database import get_session, Student, Grade, Course, letter_to_gp
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="KHS - SIAKAD", layout="wide")
require_role("mahasiswa")
page_header("📊 Kartu Hasil Studi (KHS)", "Rekap nilai per mata kuliah.")

try:
    with get_session() as s:
        st_row = s.query(Student).filter_by(user_id=st.session_state.user_id).first()
        if not st_row:
            st.warning("Profil mahasiswa belum lengkap."); st.stop()
        grades = (s.query(Grade, Course).join(Course, Course.id == Grade.course_id)
                  .filter(Grade.student_id == st_row.id).all())
        rows = [{
            "Kode": c.code, "Mata Kuliah": c.name, "SKS": c.sks,
            "Nilai": round(g.score, 1), "Huruf": g.letter,
            "Bobot": letter_to_gp(g.letter),
            "Mutu (SKS × Bobot)": round(c.sks * letter_to_gp(g.letter), 2),
        } for g, c in grades]
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat data: {e}"); rows = []

df = pd.DataFrame(rows)
if df.empty:
    st.info("Belum ada nilai yang tercatat.")
else:
    total_sks = int(df["SKS"].sum())
    total_mutu = float(df["Mutu (SKS × Bobot)"].sum())
    ipk = round(total_mutu / total_sks, 2) if total_sks else 0.0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total SKS", total_sks)
    c2.metric("Total Mutu", round(total_mutu, 2))
    c3.metric("IPK", ipk)
    st.dataframe(df, use_container_width=True, hide_index=True)

footer()
