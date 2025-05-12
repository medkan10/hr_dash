# utils/auth_guard.py
import streamlit as st

def login_required():
    if "user" not in st.session_state:
        st.warning("🚫 You must log in to access this page.")
        st.stop()
