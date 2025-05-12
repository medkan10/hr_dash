import streamlit as st
import importlib
from auth import login, logout  # You should already have this
from streamlit_extras.switch_page_button import switch_page  # optional for navigation buttons
import os

st.set_page_config(page_title="CSA Regularization Project Dashboard", layout="wide")

# Role-based page definitions
PAGE_CONFIG = {
    "admin": {
        "Dashboard": "dashboard",
        "Add Employee": "add_employee",
        "Manage Employees": "manage_employees",
        "Attendance": "attendance",
        "Reclassification": "reclassification",
        "Users": "users"  # Optional admin-only page
    },
    "editor": {
        "Dashboard": "dashboard",
        "Add Employee": "add_employee",
        "Manage Employees": "manage_employees",
        "Attendance": "attendance",
        "Reclassification": "reclassification"
    },
    "viewer": {
        "Dashboard": "dashboard"
    }
}

# Main control flow
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    role = st.session_state["user"]["role"]
    username = st.session_state["user"]["username"]
    
    st.sidebar.title(f"👋 Welcome, {username}")
    st.sidebar.caption(f"Role: `{role}`")

    # Navigation based on role
    allowed_pages = PAGE_CONFIG.get(role, {})
    page_choice = st.sidebar.radio("📂 Application Menu", list(allowed_pages.keys()))

    # Load and run selected page
    module_name = allowed_pages[page_choice]
    module = importlib.import_module(module_name)
    module.run()

    # Logout button
    if st.sidebar.button("🚪 Logout"):
        logout()
