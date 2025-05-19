import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
from datetime import datetime

# Get current user (fallback if not set)
current_user = st.session_state.get("user", {}).get("username", "system")

def run():
    st.title("✏️ Edit Employee")
    engine = get_engine()

    df = pd.read_sql("SELECT * FROM employee_data ORDER BY id DESC", engine)

    if df.empty:
        st.info("No employees found.")
        return

    selected_id = st.selectbox(
        "Select an Employee by ID",
        df['id'],
        format_func=lambda x: f"{x} - {df[df['id'] == x]['first_name'].values[0]} {df[df['id'] == x]['last_name'].values[0]}"
    )

    employee = df[df["id"] == selected_id].iloc[0]

    def safe_value(col, default=""):
        return employee[col] if pd.notna(employee[col]) else default

    sex_options = ["Male", "Female", "Other"]
    cat_options = ["Current Employee", "New Employee"]
    default_sex = safe_value("sex", "Male") if safe_value("sex", "Male") in sex_options else "Male"
    default_cat = safe_value("category", "Current Employee") if safe_value("category", "Current Employee") in cat_options else "Current Employee"
    
    with st.form("edit_employee_form"):
        first_name = st.text_input("First Name", safe_value("first_name"), disabled=True)
        middle_name = st.text_input("Middle Name", safe_value("middle_name"), disabled=True)
        last_name = st.text_input("Last Name", safe_value("last_name"), disabled=True)
        sex = st.selectbox("Sex", sex_options, index=sex_options.index(default_sex))
        grade = st.text_input("Grade", safe_value("grade"))
        qualification = st.text_input("Qualification", safe_value("qualification"))
        qualification_2 = st.text_input("Qualification", placeholder="Optional Qualification 1")
        qualification_3 = st.text_input("Qualification", placeholder="Optional Qualification 2")
        current_position = st.text_input("Current Position", safe_value("current_position"), disabled=True)
        gross_salary = st.number_input("Gross Salary", value=float(safe_value("gross_salary", 0)), disabled=True)
        dob = st.date_input("Date of Birth", pd.to_datetime(safe_value("dob", "2000-01-01")), min_value=pd.to_datetime("1900-01-01"), max_value=pd.to_datetime("today"))
        doe = st.date_input("Date of Employment", pd.to_datetime(safe_value("doe", "2020-01-01")), min_value=pd.to_datetime("1900-01-01"), max_value=pd.to_datetime("today"))
        nir_number = st.text_input("NIR Number", safe_value("nir_number"))
        county = st.text_input("County of Assignment", safe_value("county_of_assignment"))
        department = st.text_input("Department", safe_value("department"))
        category = st.selectbox("Category", cat_options, index=cat_options.index(default_cat))

        submitted = st.form_submit_button("Update Employee")

        if submitted:
            now = datetime.now()
            updated_on = now.strftime("%Y-%m-%d")
            updated_at = now.strftime("%H:%M:%S")

            try:
                update_query = text("""
                    UPDATE employee_data
                    SET first_name = :first_name,
                        middle_name = :middle_name,
                        last_name = :last_name,
                        sex = :sex,
                        grade = :grade,
                        qualification = :qualification,
                        qualification_2 = :qualification_2,
                        qualification_3 = :qualification_3,           
                        current_position = :current_position,
                        gross_salary = :gross_salary,
                        dob = :dob,
                        doe = :doe,
                        nir_number = :nir_number,
                        county_of_assignment = :county_of_assignment,
                        department = :department,
                        category = :category,
                        updated_by = :updated_by,
                        updated_on = :updated_on,
                        updated_at = :updated_at
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
                        "qualification_2": qualification_2,
                        "qualification_3": qualification_3,
                        "current_position": current_position,
                        "gross_salary": gross_salary,
                        "dob": dob,
                        "doe": doe,
                        "nir_number": nir_number,
                        "county_of_assignment": county,
                        "department": department,
                        "category": category,
                        "updated_by": current_user,
                        "updated_on": updated_on,
                        "updated_at": updated_at
                    })
                st.success("✅ Employee updated successfully.")
            except Exception as e:
                st.error("❌ Failed to update employee.")
                st.exception(e)

    st.markdown("### 📋 All Employees")
    try:
        df = pd.read_sql("SELECT * FROM employee_data ORDER BY updated_at DESC", get_engine())
        st.dataframe(df)
    except Exception as e:
        st.error("⚠️ Could not load employee table. Check your database.")
        st.exception(e)