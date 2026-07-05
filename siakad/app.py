"""
SIAKAD - STMIK Amikom Surakarta
Main Streamlit entry point (Login + Router).
Proyek Kelompok 6.
"""
from __future__ import annotations

import streamlit as st
import bcrypt

from database import init_db, get_session, User
from seed import seed as run_seed

# ------------------------------------------------------------------ #
# App configuration
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="SIAKAD - STMIK Amikom Surakarta",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0046FF"
BG      = "#1F2229"
PANEL   = "#2A2E36"
TEXT    = "#F5F6FA"

CUSTOM_CSS = f"""
<style>
  .stApp {{ background-color: {BG}; color: {TEXT}; }}
  section[data-testid="stSidebar"] {{ background-color: #171A20; }}
  h1, h2, h3, h4 {{ color: {TEXT}; }}
  .brand-title {{
    color: {PRIMARY}; font-weight: 800; font-size: 1.35rem;
    letter-spacing: .3px; margin-bottom: .25rem;
  }}
  .brand-sub {{ color: #B8BDC7; font-size: .82rem; margin-bottom: 1rem; }}
  div.stButton > button[kind="primary"],
  div.stButton > button:first-child {{
    background-color: {PRIMARY} !important;
    color: white !important;
    border: 0 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
  }}
  div.stButton > button:hover {{ filter: brightness(1.1); }}
  .panel {{
    background: {PANEL}; padding: 1.1rem 1.25rem; border-radius: 12px;
    border: 1px solid #363B45;
  }}
  .kpi {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #0033B8 100%);
    color: white; padding: 1rem 1.25rem; border-radius: 12px;
  }}
  .kpi h2 {{ color: white; margin: 0; font-size: 1.9rem; }}
  .kpi p {{ margin: 0; opacity: .85; }}
  .footer {{
    text-align: center; color: #9AA0AA; font-size: .8rem;
    padding: 1.25rem 0 .25rem 0; border-top: 1px solid #2E323B;
    margin-top: 2rem;
  }}
  /* Horizontal scroll for wide dataframes */
  div[data-testid="stDataFrame"] {{ overflow-x: auto; }}
  input, textarea, select {{ color: {TEXT} !important; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ #
# Bootstrap DB
# ------------------------------------------------------------------ #
@st.cache_resource(show_spinner=False)
def _bootstrap() -> bool:
    init_db()
    try:
        run_seed()
    except Exception as e:  # noqa: BLE001
        print(f"Seed skipped: {e}")
    return True


_bootstrap()


# ------------------------------------------------------------------ #
# Session state defaults
# ------------------------------------------------------------------ #
for k, v in {
    "logged_in": False,
    "user_id": None,
    "username": None,
    "role": None,
    "full_name": None,
}.items():
    st.session_state.setdefault(k, v)


def render_footer() -> None:
    st.markdown(
        '<div class="footer">Proyek Kelompok 6 &middot; '
        'SIAKAD STMIK Amikom Surakarta &copy; 2025</div>',
        unsafe_allow_html=True,
    )


def render_brand(sidebar: bool = True) -> None:
    target = st.sidebar if sidebar else st
    target.markdown(
        '<div class="brand-title">🎓 SIAKAD</div>'
        '<div class="brand-sub">STMIK Amikom Surakarta</div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ #
# Authentication
# ------------------------------------------------------------------ #
def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def do_login(username: str, password: str) -> tuple[bool, str]:
    if not username or not password:
        return False, "Username dan password wajib diisi."
    try:
        with get_session() as s:
            user = s.query(User).filter_by(username=username.strip()).first()
            if not user or not verify_password(password, user.password_hash):
                return False, "Username atau password salah."
            st.session_state.logged_in = True
            st.session_state.user_id   = user.id
            st.session_state.username  = user.username
            st.session_state.role      = user.role
            st.session_state.full_name = user.full_name
            return True, "Login berhasil."
    except Exception as e:  # noqa: BLE001
        return False, f"Kesalahan sistem: {e}"


def do_logout() -> None:
    for k in ("logged_in", "user_id", "username", "role", "full_name"):
        st.session_state[k] = False if k == "logged_in" else None


# ------------------------------------------------------------------ #
# Login screen
# ------------------------------------------------------------------ #
def login_view() -> None:
    render_brand(sidebar=False)
    st.markdown("## Masuk ke SIAKAD")
    st.caption("Silakan masuk sesuai peran Anda (Admin / Dosen / Mahasiswa).")

    col1, col2 = st.columns([1.1, 1])
    with col1:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="mis. admin")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk", type="primary",
                                              use_container_width=True)
        if submitted:
            ok, msg = do_login(username, password)
            (st.success if ok else st.error)(msg)
            if ok:
                st.rerun()

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### Akun Demo")
        st.markdown(
            "- **Admin** — `admin` / `admin123`\n"
            "- **Dosen** — `dosen1` / `dosen123`\n"
            "- **Mahasiswa** — `mahasiswa1` / `mhs123`"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# ------------------------------------------------------------------ #
# Home dashboard (post login)
# ------------------------------------------------------------------ #
def home_view() -> None:
    render_brand()
    st.sidebar.markdown(f"**{st.session_state.full_name}**")
    st.sidebar.caption(f"Peran: {st.session_state.role.title()}")
    if st.sidebar.button("Keluar", use_container_width=True):
        do_logout()
        st.rerun()

    st.sidebar.markdown("---")
    role = st.session_state.role
    st.sidebar.markdown("### Navigasi")
    if role == "admin":
        st.sidebar.page_link("pages/1_Admin_Dashboard.py", label="🛠️ Admin Dashboard")
        st.sidebar.page_link("pages/2_Manage_Students.py", label="👨‍🎓 Kelola Mahasiswa")
        st.sidebar.page_link("pages/3_Manage_Lecturers.py", label="👩‍🏫 Kelola Dosen")
        st.sidebar.page_link("pages/4_Manage_Courses.py", label="📘 Kelola Mata Kuliah")
    elif role == "dosen":
        st.sidebar.page_link("pages/5_Dosen_Dashboard.py", label="📚 Dashboard Dosen")
        st.sidebar.page_link("pages/6_Dosen_Attendance.py", label="🗓️ Input Presensi")
        st.sidebar.page_link("pages/7_Dosen_Grades.py", label="📝 Input Nilai")
    elif role == "mahasiswa":
        st.sidebar.page_link("pages/8_Mahasiswa_Dashboard.py", label="🏠 Dashboard")
        st.sidebar.page_link("pages/9_Mahasiswa_KRS.py", label="📄 Isi KRS")
        st.sidebar.page_link("pages/10_Mahasiswa_KHS.py", label="📊 Lihat KHS")

    st.markdown("## Selamat Datang di SIAKAD")
    st.caption("STMIK Amikom Surakarta — Sistem Informasi Akademik")

    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="kpi"><p>Peran Anda</p>'
                f'<h2>{role.title()}</h2></div>', unsafe_allow_html=True)
    c2.markdown('<div class="kpi"><p>Nama</p>'
                f'<h2 style="font-size:1.2rem">{st.session_state.full_name}</h2></div>',
                unsafe_allow_html=True)
    c3.markdown('<div class="kpi"><p>Username</p>'
                f'<h2 style="font-size:1.4rem">{st.session_state.username}</h2></div>',
                unsafe_allow_html=True)

    st.markdown(" ")
    st.info("Gunakan menu di sidebar kiri untuk membuka modul sesuai peran Anda.")
    render_footer()


# ------------------------------------------------------------------ #
# Router
# ------------------------------------------------------------------ #
if not st.session_state.logged_in:
    login_view()
else:
    home_view()
