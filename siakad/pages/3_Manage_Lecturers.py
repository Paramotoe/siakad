import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import bcrypt
from database import get_session, User, Lecturer
from pages._shared import page_header, footer, require_role

st.set_page_config(page_title="Kelola Dosen - SIAKAD", layout="wide")
require_role("admin")
page_header("👩‍🏫 Kelola Dosen", "CRUD data dosen.")

def load() -> pd.DataFrame:
    try:
        with get_session() as s:
            rows = s.query(Lecturer).join(User).all()
            return pd.DataFrame([{
                "ID": l.id, "NIDN": l.nidn, "Nama": l.user.full_name,
                "Username": l.user.username, "Departemen": l.department,
            } for l in rows])
    except Exception as e:  # noqa: BLE001
        st.error(f"Gagal memuat: {e}")
        return pd.DataFrame()

t1, t2, t3, t4 = st.tabs(["📋 Daftar", "➕ Tambah", "✏️ Ubah", "🗑️ Hapus"])

with t1:
    st.dataframe(load(), use_container_width=True, hide_index=True)

with t2:
    with st.form("add_l", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nidn = c1.text_input("NIDN *")
        username = c2.text_input("Username *")
        name = c1.text_input("Nama Lengkap *")
        password = c2.text_input("Password *", type="password")
        dept = c1.text_input("Departemen", value="Teknik Informatika")
        ok = st.form_submit_button("Simpan", type="primary")
    if ok:
        if not all([nidn.strip(), username.strip(), name.strip(), password]):
            st.error("Field wajib belum lengkap.")
        else:
            try:
                with get_session() as s:
                    if s.query(User).filter_by(username=username.strip()).first():
                        st.error("Username dipakai."); st.stop()
                    if s.query(Lecturer).filter_by(nidn=nidn.strip()).first():
                        st.error("NIDN terdaftar."); st.stop()
                    u = User(username=username.strip(), full_name=name.strip(),
                             role="dosen",
                             password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())
                    s.add(u); s.flush()
                    s.add(Lecturer(user_id=u.id, nidn=nidn.strip(), department=dept.strip()))
                st.success("Dosen ditambahkan."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal: {e}")

with t3:
    df = load()
    if df.empty:
        st.info("Belum ada data.")
    else:
        sel = st.selectbox("Pilih dosen", options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'NIDN'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}")
        row = df[df["ID"] == sel].iloc[0]
        with st.form("edit_l"):
            name = st.text_input("Nama", value=row["Nama"])
            dept = st.text_input("Departemen", value=row["Departemen"])
            ok = st.form_submit_button("Perbarui", type="primary")
        if ok:
            try:
                with get_session() as s:
                    lec = s.get(Lecturer, int(sel))
                    if lec is None:
                        st.error("Tidak ditemukan."); st.stop()
                    lec.user.full_name = name.strip()
                    lec.department = dept.strip()
                st.success("Diperbarui."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal: {e}")

with t4:
    df = load()
    if df.empty:
        st.info("Belum ada data.")
    else:
        sel = st.selectbox("Pilih untuk dihapus", options=df["ID"].tolist(),
                           format_func=lambda i: f"{df.loc[df['ID']==i,'NIDN'].iat[0]} — {df.loc[df['ID']==i,'Nama'].iat[0]}",
                           key="del_l")
        confirm = st.checkbox("Konfirmasi hapus akun beserta relasinya.")
        if st.button("Hapus", type="primary", disabled=not confirm):
            try:
                with get_session() as s:
                    lec = s.get(Lecturer, int(sel))
                    if lec:
                        s.delete(lec.user)
                st.success("Dihapus."); st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Gagal: {e}")

footer()
