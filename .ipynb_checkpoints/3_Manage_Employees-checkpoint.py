import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Please login to access this page.")
#     st.stop()

def run():

    st.title("🛠️ Manage Employees")
    
    engine = get_engine()
    
    # Fetch employee records
    df = pd.read_sql("SELECT * FROM employee_data ORDER BY id DESC", engine)
    
    # Select employee to edit or delete
    selected_id = st.selectbox("Select an Employee by ID", df['id'], format_func=lambda x: f"{x} - {df[df['id'] == x]['first_name'].values[0]} {df[df['id'] == x]['last_name'].values[0]}")
    
    # Load current data
    employee = df[df["id"] == selected_id].iloc[0]
    
    # Editable fields
    with st.form("edit_employee_form"):
        st.subheader("✏️ Edit Employee")
        first_name = st.text_input("First Name", employee["first_name"])
        middle_name = st.text_input("Middle Name", employee["middle_name"])
        last_name = st.text_input("Last Name", employee["last_name"])
        sex = st.selectbox("Sex", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(employee["sex"]))
        grade = st.text_input("Grade", employee["grade"])
        qualification = st.text_input("Qualification", employee["qualification"])
        current_position = st.text_input("Current Position", employee["current_position"])
        gross_salary = st.number_input("Gross Salary", value=float(employee["gross_salary"]))
        dob = st.date_input("Date of Birth", pd.to_datetime(employee["dob"]))
        doe = st.date_input("Date of Employment", pd.to_datetime(employee["doe"]))
        nir_number = st.text_input("NIR Number", employee["nir_number"])
        county = st.text_input("County of Assignment", employee["county_of_assignment"])
        department = st.text_input("Department", employee["department"])
        category = st.text_input("Category", employee["category"])
    
        submitted = st.form_submit_button("Update Employee")
    
        if submitted:
            update_query = text("""
                UPDATE employee_data
                SET first_name = :first_name,
                    middle_name = :middle_name,
                    last_name = :last_name,
                    sex = :sex,
                    grade = :grade,
                    qualification = :qualification,
                    current_position = :current_position,
                    gross_salary = :gross_salary,
                    dob = :dob,
                    doe = :doe,
                    nir_number = :nir_number,
                    county_of_assignment = :county_of_assignment,
                    department = :department,
                    category = :category
                WHERE id = :id
            """)
            with engine.begin() as conn:
                conn.execute(update_query, {
                    "id": selected_id,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "sex": sex,
                    "grade": grade,
                    "qualification": qualification,
                    "current_position": current_position,
                    "gross_salary": gross_salary,
                    "dob": dob,
                    "doe": doe,
                    "nir_number": nir_number,
                    "county_of_assignment": county,
                    "department": department,
                    "category": category
                })
            st.success("✅ Employee updated successfully.")
    
    # Delete section
    if st.button("🗑️ Delete Employee"):
        delete_query = text("DELETE FROM employee_data WHERE id = :id")
        with engine.begin() as conn:
            conn.execute(delete_query, {"id": selected_id})
        st.success("🗑️ Employee deleted successfully. Please refresh to see changes.")
