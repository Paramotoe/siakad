"""Shared helpers for Streamlit pages."""
from __future__ import annotations

import streamlit as st

PRIMARY = "#0046FF"
BG      = "#1F2229"
PANEL   = "#2A2E36"
TEXT    = "#F5F6FA"

CUSTOM_CSS = f"""
<style>
  .stApp {{ background-color: {BG}; color: {TEXT}; }}
  section[data-testid="stSidebar"] {{ background-color: #171A20; }}
  h1, h2, h3, h4 {{ color: {TEXT}; }}
  .brand-title {{ color: {PRIMARY}; font-weight: 800; font-size: 1.35rem;
                  margin-bottom:.25rem; }}
  .brand-sub {{ color:#B8BDC7; font-size:.82rem; margin-bottom:1rem; }}
  div.stButton > button:first-child {{
    background-color:{PRIMARY} !important; color:white !important;
    border:0 !important; border-radius:8px !important; font-weight:600 !important;
  }}
  .panel {{ background:{PANEL}; padding:1.1rem 1.25rem; border-radius:12px;
            border:1px solid #363B45; }}
  .footer {{ text-align:center; color:#9AA0AA; font-size:.8rem;
             padding:1.25rem 0 .25rem 0; border-top:1px solid #2E323B;
             margin-top:2rem; }}
  div[data-testid="stDataFrame"] {{ overflow-x:auto; }}
</style>
"""


def apply_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def brand_sidebar() -> None:
    st.sidebar.markdown(
        '<div class="brand-title">🎓 SIAKAD</div>'
        '<div class="brand-sub">STMIK Amikom Surakarta</div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        '<div class="footer">Proyek Kelompok 6 &middot; '
        'SIAKAD STMIK Amikom Surakarta &copy; 2025</div>',
        unsafe_allow_html=True,
    )


def require_role(*allowed: str) -> bool:
    if not st.session_state.get("logged_in"):
        st.error("Anda belum login. Kembali ke halaman utama.")
        st.page_link("app.py", label="⬅️ Ke halaman login")
        st.stop()
    if st.session_state.get("role") not in allowed:
        st.error("Akses ditolak — halaman ini bukan untuk peran Anda.")
        st.page_link("app.py", label="⬅️ Kembali")
        st.stop()
    return True


def page_header(title: str, subtitle: str = "") -> None:
    apply_theme()
    brand_sidebar()
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
