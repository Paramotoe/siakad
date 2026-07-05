import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time as dtime
import streamlit as st
import pandas as pd
from database import get_session, Course, Lecturer, User
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Kelola Mata Kuliah - SIAKAD", layout="wide")
require_role("admin")
page_header("📘 Kelola Mata Kuliah", "CRUD mata kuliah + jadwal.")

DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]

def load() -> pd.DataFrame:
    try:
        with get_session() as s:
            rows = s.query(Course).all()
            return pd.DataFrame([{
                "ID": c.id, "Kode": c.code, "Nama": c.name, "SKS": c.sks,
                "Semester": c.semester,
                "Dosen": c.lecturer.user.full_name if c.lecturer else "-",
                "Hari": c.day,
                "Jam": f"{c.time_start.strftime('%H:%M') if c.time_start else '-'} - "
                       f"{c.time_end.strftime('%H:%M') if c.time_end else '-'}",
                "Ruang": c.room,
            } for c in rows])
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal memuat: {e}")
        return pd.DataFrame()

def lecturer_options() -> dict[int, str]:
    with get_session() as s:
        return {l.id: f"{l.nidn} — {l.user.full_name}"
                for l in s.query(Lecturer).join(User).all()}

t1, t2, t3, t4 = st.tabs(["📋 Daftar", "➕ Tambah", "✏️ Ubah", "🗑️ Hapus"])

with t1:
    st.dataframe(load(), use_container_width=True, hide_index=True)

with t2:
    lect_opts = lecturer_options()
    with st.form("add_c", clear_on_submit=True):
        c1, c2 = st.columns(2)
        code = c1.text_input("Kode MK *")
        name = c2.text_input("Nama MK *")
        sks = c1.number_input("SKS", 1, 6, 3)
        semester = c2.number_input("Semester", 1, 14, 1)
        lect_id = c1.selectbox("Dosen Pengampu",
                               options=[None] + list(lect_opts.keys()),
                               format_func=lambda x: "— Belum dipilih —" if x is None else lect_opts[x])
        day = c2.selectbox("Hari", DAYS)
        t_start = c1.time_input("Jam Mulai", value=dtime(8, 0))
        t_end = c2.time_input("Jam Selesai", value=dtime(10, 30))
        room = c1.text_input("Ruang", value="R.101")
        ok = st.form_submit_button("Simpan", type="primary")
    if ok:
        if not code.strip() or not name.strip():
            st.error("Kode & nama wajib.")
        elif t_end <= t_start:
            st.error("Jam selesai harus setelah jam mulai.")
        else:
            try:
                with get_session() as s:
                    if s.query(Course).filter_by(code=code.strip()).first():
                        st.error("Kode MK sudah ada."); st.stop()
                    s.add(Course(code=code.strip(), name=name.strip(),
                                 sks=int(sks), semester=int(semester),
                                 lecturer_id=lect_id, day=day,
                                 time_start=t_start, time_end=t_end,
                                 room=room.strip() or "-"))
                st.success("MK ditambahkan."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal: {e}")

with t3:
    df = load()
    if df.empty:
        st.info("Belum ada MK.")
    else:
        lect_opts = lecturer_options()
        sel = st.selectbox("Pilih MK", options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'Kode'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}")
        with get_session() as s:
            cur = s.get(Course, int(sel))
            if cur is None:
                st.error("Tidak ditemukan."); st.stop()
            cur_data = {
                "name": cur.name, "sks": cur.sks, "semester": cur.semester,
                "lecturer_id": cur.lecturer_id, "day": cur.day,
                "time_start": cur.time_start or dtime(8, 0),
                "time_end": cur.time_end or dtime(10, 30),
                "room": cur.room,
            }
        with st.form("edit_c"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nama", value=cur_data["name"])
            sks = c2.number_input("SKS", 1, 6, cur_data["sks"])
            semester = c1.number_input("Semester", 1, 14, cur_data["semester"])
            lect_id = c2.selectbox("Dosen",
                                   options=[None] + list(lect_opts.keys()),
                                   index=([None] + list(lect_opts.keys())).index(cur_data["lecturer_id"])
                                         if cur_data["lecturer_id"] in lect_opts else 0,
                                   format_func=lambda x: "—" if x is None else lect_opts[x])
            day = c1.selectbox("Hari", DAYS, index=DAYS.index(cur_data["day"]) if cur_data["day"] in DAYS else 0)
            t_start = c2.time_input("Jam Mulai", value=cur_data["time_start"])
            t_end = c1.time_input("Jam Selesai", value=cur_data["time_end"])
            room = c2.text_input("Ruang", value=cur_data["room"])
            ok = st.form_submit_button("Perbarui", type="primary")
        if ok:
            if t_end <= t_start:
                st.error("Jam selesai harus setelah jam mulai.")
            else:
                try:
                    with get_session() as s:
                        c = s.get(Course, int(sel))
                        c.name = name.strip(); c.sks = int(sks)
                        c.semester = int(semester); c.lecturer_id = lect_id
                        c.day = day; c.time_start = t_start; c.time_end = t_end
                        c.room = room.strip() or "-"
                    st.success("Diperbarui."); st.rerun()
                except Exception as e:  # noqa: BLE001
                    st.error(f"Gagal: {e}")

with t4:
    df = load()
    if df.empty:
        st.info("Belum ada MK.")
    else:
        sel = st.selectbox("Pilih untuk dihapus", options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'Kode'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}",
                           key="delc")
        confirm = st.checkbox("Konfirmasi hapus MK beserta KRS/nilai terkait.")
        if st.button("Hapus", type="primary", disabled=not confirm):
            try:
                with get_session() as s:
                    c = s.get(Course, int(sel))
                    if c: s.delete(c)
                st.success("Dihapus."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal: {e}")

footer()
