import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
from auth import register_user



def run():

    st.title("👥 User Management")
    
    # Access Control
    # if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    #     st.warning("Please log in to view this page.")
    #     st.stop()
    
    # Only allow admins to register new users
    # if "user" not in st.session_state or st.session_state["user"].get("role") != "admin":
    #     st.warning("⛔ Access denied. Admins only.")
    #     st.stop()
    
    
    st.subheader("➕ Register New User")
    
    with st.form("register_form"):
        first_name = st.text_input("First Name")
        middle_name = st.text_input("Middle Name") 
        last_name = st.text_input("Last Name")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["Admin", "Editor", "Viewer", "Attendance Officer", "Reclassifier"])
        submit_btn = st.form_submit_button("Register")
    
        if submit_btn:
            if not new_username or not new_password or not first_name or not  last_name:
                st.warning("Please fill out all fields.")
            else:
                try:
                    register_user(first_name, middle_name, last_name, new_username, new_password, new_role)
                    st.success(f"✅ User '{first_name}' registered successfully!")
                except Exception as e:
                    st.error("Error registering user. Username may already exist.")
                    st.exception(e)
    
    # View + Delete Users
    st.subheader("📋 All Users")
    
    try:
        users_df = pd.read_sql("SELECT id, first_name, last_name, username, role FROM users", get_engine())
        for _, row in users_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            col1.write(row["first_name"])
            col2.write(row["last_name"])
            col3.write(row["username"])
            col4.write(row["role"])
            delete_btn = col5.button("🗑️ Delete", key=f"delete_{row['id']}")
    
            if delete_btn:
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": row["id"]})
                st.success(f"User {row['username']} deleted successfully.")
                st.rerun()
    except Exception as e:
        st.error("Failed to load users.")
        st.exception(e)
