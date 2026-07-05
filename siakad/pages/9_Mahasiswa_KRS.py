import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from database import get_session, Student, KRS, Course
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="KRS - SIAKAD", layout="wide")
require_role("mahasiswa")
page_header("📄 Kartu Rencana Studi (KRS)", "Pilih mata kuliah untuk semester ini.")

MAX_SKS = 24

try:
    with get_session() as s:
        st_row = s.query(Student).filter_by(user_id=st.session_state.user_id).first()
        if not st_row:
            st.warning("Profil mahasiswa belum lengkap."); st.stop()
        offered = s.query(Course).filter(Course.semester <= st_row.semester).all()
        taken_ids = {k.course_id for k in
                     s.query(KRS).filter_by(student_id=st_row.id).all()}
        offered_data = [{
            "id": c.id, "code": c.code, "name": c.name, "sks": c.sks,
            "sem": c.semester, "day": c.day,
            "time": f"{c.time_start.strftime('%H:%M') if c.time_start else '-'} - "
                    f"{c.time_end.strftime('%H:%M') if c.time_end else '-'}",
            "room": c.room,
            "dosen": c.lecturer.user.full_name if c.lecturer else "-",
        } for c in offered]
        student_id = st_row.id
except Exception as e:  # noqa: BLE001
    st.error(f"Gagal memuat data: {e}"); st.stop()

st.caption(f"Maksimum {MAX_SKS} SKS per semester. MK yang sudah diambil dicentang.")
df = pd.DataFrame(offered_data)
df["Ambil"] = df["id"].isin(taken_ids)
df_show = df[["Ambil", "code", "name", "sks", "sem", "dosen", "day", "time", "room"]].rename(
    columns={"code":"Kode","name":"Nama","sks":"SKS","sem":"Sem",
             "dosen":"Dosen","day":"Hari","time":"Jam","room":"Ruang"})

edited = st.data_editor(
    df_show, hide_index=True, use_container_width=True,
    disabled=["Kode","Nama","SKS","Sem","Dosen","Hari","Jam","Ruang"],
    key="krs_editor",
)

total = int(edited.loc[edited["Ambil"], "SKS"].sum())
c1, c2 = st.columns([1, 3])
c1.metric("Total SKS Terpilih", total)
if total > MAX_SKS:
    c2.error(f"Melebihi batas {MAX_SKS} SKS.")
else:
    c2.info(f"Sisa {MAX_SKS - total} SKS.")

if st.button("💾 Simpan KRS", type="primary", disabled=(total > MAX_SKS)):
    try:
        selected_ids = {int(df.iloc[i]["id"]) for i, take
                        in enumerate(edited["Ambil"].tolist()) if take}
        with get_session() as s:
            current = {k.course_id: k for k in
                       s.query(KRS).filter_by(student_id=student_id).all()}
            for cid in selected_ids - set(current.keys()):
                s.add(KRS(student_id=student_id, course_id=cid))
            for cid in set(current.keys()) - selected_ids:
                s.delete(current[cid])
        st.success("KRS berhasil disimpan."); st.rerun()
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal menyimpan: {e}")

footer()
