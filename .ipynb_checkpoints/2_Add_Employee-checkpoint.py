import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Please login to access this page.")
#     st.stop()


import streamlit as st

def run():
    st.title("👤 Add New Employee")
    
    # Create the form
    with st.form("add_employee_form"):
        first_name = st.text_input("First Name")
        middle_name = st.text_input("Middle Name")
        last_name = st.text_input("Last Name")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        grade = st.text_input("Grade")
        qualification = st.text_input("Qualification")
        current_position = st.text_input("Current Position")
        gross_salary = st.number_input("Gross Salary", min_value=0.0, step=0.01)
        dob = st.date_input("Date of Birth")
        doe = st.date_input("Date of Employment")
        nir_number = st.text_input("NIR Number")
        county = st.text_input("County of Assignment")
        department = st.text_input("Department")
        category = st.selectbox("Category", ["Current Employee", "New Employee"])
    
        submitted = st.form_submit_button("Submit")
    
        if submitted:
            # Validation
            if not first_name or not last_name or not department or not category:
                st.warning("🚫 Please fill all required fields (First Name, Last Name, Department, Category).")
            elif dob >= doe:
                st.warning("🚫 Date of Birth must be before Date of Employment.")
            elif gross_salary <= 0:
                st.warning("🚫 Gross Salary must be greater than 0.")
            else:
                query = text("""
                    INSERT INTO employee_data (
                        first_name, middle_name, last_name, current_position, sex, grade,
                        qualification, gross_salary, dob, doe, nir_number,
                        county_of_assignment, department, category
                    ) VALUES (
                        :first_name, :middle_name, :last_name, :current_position, :sex, :grade,
                        :qualification, :gross_salary, :dob, :doe, :nir_number,
                        :county_of_assignment, :department, :category
                    )
                """)
                engine = get_engine()
                with engine.begin() as conn:  # This commits automatically
                    conn.execute(query, {
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "sex": sex,
                        "grade": grade,
                        "qualification": qualification,
                        "gross_salary": gross_salary,
                        "dob": dob,
                        "doe": doe,
                        "nir_number": nir_number,
                        "county_of_assignment": county,
                        "department": department,
                        "category": category,
                        "current_position": current_position
                    })
                st.success(f"✅ {first_name} {last_name} added successfully!")
    
    # Show all employees
    st.markdown("### 📋 All Employees")
    try:
        df = pd.read_sql("SELECT * FROM employee_data ORDER BY id DESC", get_engine())
        st.dataframe(df)
    except Exception as e:
        st.error("⚠️ Could not load employee table. Check your database.")
        st.exception(e)
