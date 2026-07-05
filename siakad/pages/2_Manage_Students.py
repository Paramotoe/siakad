import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import bcrypt
from database import get_session, User, Student
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Kelola Mahasiswa - SIAKAD", layout="wide")
require_role("admin")
page_header("👨‍🎓 Kelola Mahasiswa", "CRUD data mahasiswa.")

def load_students() -> pd.DataFrame:
    try:
        with get_session() as s:
            rows = s.query(Student).join(User).all()
            return pd.DataFrame([{
                "ID": st_.id, "NIM": st_.nim, "Nama": st_.user.full_name,
                "Username": st_.user.username, "Program": st_.program,
                "Semester": st_.semester,
            } for st_ in rows])
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

tab_list, tab_add, tab_edit, tab_del = st.tabs(["📋 Daftar", "➕ Tambah", "✏️ Ubah", "🗑️ Hapus"])

with tab_list:
    df = load_students()
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab_add:
    with st.form("add_student", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nim      = c1.text_input("NIM *")
        username = c2.text_input("Username *")
        name     = c1.text_input("Nama Lengkap *")
        password = c2.text_input("Password *", type="password")
        program  = c1.text_input("Program Studi", value="Teknik Informatika")
        semester = c2.number_input("Semester", 1, 14, 1)
        ok = st.form_submit_button("Simpan", type="primary")
    if ok:
        if not all([nim.strip(), username.strip(), name.strip(), password]):
            st.error("Semua field wajib (*) harus diisi.")
        else:
            try:
                with get_session() as s:
                    if s.query(User).filter_by(username=username.strip()).first():
                        st.error("Username sudah dipakai."); st.stop()
                    if s.query(Student).filter_by(nim=nim.strip()).first():
                        st.error("NIM sudah terdaftar."); st.stop()
                    u = User(username=username.strip(), full_name=name.strip(),
                             role="mahasiswa",
                             password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())
                    s.add(u); s.flush()
                    s.add(Student(user_id=u.id, nim=nim.strip(),
                                  program=program.strip() or "Teknik Informatika",
                                  semester=int(semester)))
                st.success("Mahasiswa berhasil ditambahkan.")
                st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal menyimpan: {e}")

with tab_edit:
    df = load_students()
    if df.empty:
        st.info("Belum ada data.")
    else:
        sel = st.selectbox("Pilih mahasiswa",
                           options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'NIM'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}")
        row = df[df["ID"] == sel].iloc[0]
        with st.form("edit_student"):
            name = st.text_input("Nama", value=row["Nama"])
            program = st.text_input("Program", value=row["Program"])
            semester = st.number_input("Semester", 1, 14, int(row["Semester"]))
            ok = st.form_submit_button("Perbarui", type="primary")
        if ok:
            try:
                with get_session() as s:
                    st_obj = s.get(Student, int(sel))
                    if st_obj is None:
                        st.error("Data tidak ditemukan."); st.stop()
                    st_obj.user.full_name = name.strip()
                    st_obj.program = program.strip()
                    st_obj.semester = int(semester)
                st.success("Data diperbarui."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal memperbarui: {e}")

with tab_del:
    df = load_students()
    if df.empty:
        st.info("Belum ada data.")
    else:
        sel = st.selectbox("Pilih untuk dihapus",
                           options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'NIM'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}",
                           key="del_sel")
        confirm = st.checkbox("Saya yakin ingin menghapus akun beserta datanya.")
        if st.button("Hapus", type="primary", disabled=not confirm):
            try:
                with get_session() as s:
                    st_obj = s.get(Student, int(sel))
                    if st_obj:
                        s.delete(st_obj.user)  # cascade hapus student
                st.success("Data dihapus."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal menghapus: {e}")

footer()
