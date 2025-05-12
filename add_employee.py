import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
from datetime import datetime

def run():
    st.title("👤 Add New Employee")

    # Get current user (fallback if not set)
    current_user = st.session_state.get("user", {}).get("username", "system")

    # Create the form
    with st.form("add_employee_form"):
        first_name = st.text_input("First Name")
        middle_name = st.text_input("Middle Name")
        last_name = st.text_input("Last Name")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        grade = st.text_input("Grade")
        qualification = st.text_input("Qualification", placeholder="Leave blank for 'No Qualification'")
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
            qualification = qualification if qualification.strip() else "No Qualification"
            created_on = datetime.today().date()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Validation
            if not first_name or not last_name or not department or not category:
                st.warning("🚫 Please fill all required fields (First Name, Last Name, Department, Category).")
            elif dob >= doe:
                st.warning("🚫 Date of Birth must be before Date of Employment.")
            elif gross_salary <= 0:
                st.warning("🚫 Gross Salary must be greater than 0.")
            elif not nir_number.isdigit() or len(nir_number) != 10:
                st.warning("🚫 NIR Number must be exactly 10 digits.")
            else:
                engine = get_engine()
                with engine.begin() as conn:
                    # Check if NIR already exists
                    result = conn.execute(
                        text("SELECT first_name, last_name FROM employee_data WHERE nir_number = :nir"),
                        {"nir": nir_number}
                    ).fetchone()

                    if result:
                        existing_name = f"{result.first_name} {result.last_name}"
                        st.error(f"🚫 This NIR number is already in use by {existing_name}.")
                    else:
                        query = text("""
                            INSERT INTO employee_data (
                                first_name, middle_name, last_name, current_position, sex, grade,
                                qualification, gross_salary, dob, doe, nir_number,
                                county_of_assignment, department, category,
                                created_by, created_on, created_at
                            ) VALUES (
                                :first_name, :middle_name, :last_name, :current_position, :sex, :grade,
                                :qualification, :gross_salary, :dob, :doe, :nir_number,
                                :county_of_assignment, :department, :category,
                                :created_by, :created_on, :created_at
                            )
                        """)
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
                            "current_position": current_position,
                            "created_by": current_user,
                            "created_on": created_on,
                            "created_at": created_at
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
