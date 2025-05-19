import streamlit as st
import importlib
from auth import login, logout  # You should already have this
# from streamlit_extras.switch_page_button import switch_page  # optional for navigation buttons
import os

st.set_page_config(page_title="CSA Regularization Project Dashboard", layout="wide")

# Role-based page definitions
PAGE_CONFIG = {
    "Admin": {
        "Welcome": "welcome",
        "Dashboard": "dashboard",
        "Add Employee": "add_employee",
        "Edit Employees": "edit_employees",
        "Attendance": "attendance",
        "Reclassification": "reclassification",
        # Exclusive to Admin
        "Delete Employees": "delete_employee",
        "Trash Management": "trash_management",
        "Bulk Upload": "bulk_upload",
        "Users": "users",  # Optional admin-only page
        "Clear Database": "delete_all" 
    },
    "Editor": {
        "Welcome": "welcome",
        "Dashboard": "dashboard",
        "Add Employee": "add_employee",
        "Edit Employees": "edit_employees",
        "Attendance": "attendance",
        "Reclassification": "reclassification"
    },
    "Viewer": {
        "Welcome": "welcome",
        "Dashboard": "dashboard"
    },
    "Attendance Officer": {
        "Welcome": "welcome",
        "Dashboard": "dashboard",
        "Attendance": "attendance"
    },
    "Reclassifier": {
        "Welcome": "welcome",
        "Dashboard": "dashboard",
        "Reclassification": "reclassification"
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
    first_name = st.session_state["user"]["first_name"]

    st.sidebar.image("images.jpeg")
    st.sidebar.title(f"👋 Welcome, {first_name}")
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
