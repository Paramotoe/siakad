import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from database import (get_session, Lecturer, Course, KRS, Student, Grade,
                       score_to_letter)
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Input Nilai - SIAKAD", layout="wide")
require_role("dosen")
page_header("📝 Input Nilai Akhir", "Input nilai akhir per mata kuliah.")

try:
    with get_session() as s:
        lec = s.query(Lecturer).filter_by(user_id=st.session_state.user_id).first()
        if not lec:
            st.warning("Profil dosen belum lengkap."); st.stop()
        classes = s.query(Course).filter_by(lecturer_id=lec.id).all()
        if not classes:
            st.info("Anda belum mengampu kelas."); footer(); st.stop()
        cmap = {c.id: f"{c.code} — {c.name}" for c in classes}
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat kelas: {e}"); st.stop()

course_id = st.selectbox("Kelas", options=list(cmap.keys()),
                         format_func=lambda i: cmap[i])

try:
    with get_session() as s:
        peserta = (s.query(Student).join(KRS, KRS.student_id == Student.id)
                   .filter(KRS.course_id == course_id).all())
        existing = {g.student_id: g for g in s.query(Grade)
                    .filter_by(course_id=course_id).all()}
        rows = [{
            "student_id": st_.id, "NIM": st_.nim, "Nama": st_.user.full_name,
            "Nilai": float(existing[st_.id].score) if st_.id in existing else 0.0,
            "Huruf": existing[st_.id].letter if st_.id in existing else "E",
        } for st_ in peserta]
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat peserta: {e}"); st.stop()

if not rows:
    st.info("Belum ada peserta."); footer(); st.stop()

df = pd.DataFrame(rows)
edited = st.data_editor(
    df, hide_index=True, use_container_width=True,
    column_config={
        "student_id": None,
        "NIM": st.column_config.TextColumn(disabled=True),
        "Nama": st.column_config.TextColumn(disabled=True),
        "Nilai": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.5, format="%.1f"),
        "Huruf": st.column_config.TextColumn(disabled=True,
                    help="Otomatis dihitung dari nilai angka."),
    },
    key="grade_editor",
)

if st.button("💾 Simpan Nilai", type="primary"):
    try:
        with get_session() as s:
            for _, r in edited.iterrows():
                score = float(r["Nilai"] or 0.0)
                if score < 0 or score > 100:
                    st.error(f"Nilai {r['NIM']} tidak valid ({score})."); st.stop()
                letter = score_to_letter(score)
                g = (s.query(Grade).filter_by(student_id=int(r["student_id"]),
                                              course_id=int(course_id)).first())
                if g:
                    g.score = score; g.letter = letter
                else:
                    s.add(Grade(student_id=int(r["student_id"]),
                                course_id=int(course_id),
                                score=score, letter=letter))
        st.success("Nilai tersimpan."); st.rerun()
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal: {e}")

footer()
