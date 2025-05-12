import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
from datetime import datetime

def run():
    st.title("🗑️ Delete Employee")


    # Get current user (fallback if not set)
    current_user = st.session_state.get("user", {}).get("username", "system")

    engine = get_engine()

    try:
        df = pd.read_sql("SELECT * FROM employee_data ORDER BY id DESC", engine)
    except Exception as e:
        st.error("⚠️ Unable to load employee data.")
        st.exception(e)
        return

    if df.empty:
        st.info("No employees available.")
        return

    selected_id = st.selectbox(
        "Select an Employee by ID",
        df["id"],
        format_func=lambda x: f"{x} - {df[df['id'] == x]['first_name'].values[0]} {df[df['id'] == x]['last_name'].values[0]}"
    )

    employee = df[df["id"] == selected_id].iloc[0]

    st.subheader("👁️ Employee Details")
    st.write(employee.to_dict())

    if st.button("🔥 Delete Employee Immediately"):
        try:
            now = datetime.now()
            trash_data = {
            "id": int(employee["id"]),
            "first_name": str(employee["first_name"]),
            "middle_name": str(employee["middle_name"]),
            "last_name": str(employee["last_name"]),
            "sex": str(employee["sex"]),
            "grade": str(employee["grade"]),
            "qualification": str(employee["qualification"]),
            "current_position": str(employee["current_position"]),
            "gross_salary": float(employee["gross_salary"]) if pd.notnull(employee["gross_salary"]) else 0.0,
            "dob": str(employee["dob"]),
            "doe": str(employee["doe"]),
            "nir_number": str(employee["nir_number"]),
            "county_of_assignment": str(employee["county_of_assignment"]),
            "department": str(employee["department"]),
            "category": str(employee["category"]),
            "created_by": str(employee.get("created_by", "unknown")),
            "created_on": str(employee.get("created_on", now.date())),
            "created_at": str(employee.get("created_at", now.time())),
            "trashed_by": str(current_user),
            "trash_date": str(now.date()),
            "trash_time": str(now.time())
        }


            st.write("📦 Data to Trash:", trash_data)

            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO trash (
                        id, first_name, middle_name, last_name, sex, grade,
                        qualification, current_position, gross_salary, dob, doe,
                        nir_number, county_of_assignment, department, category,
                        created_by, created_on, created_at,
                        trashed_by, trash_date, trash_time
                    ) VALUES (
                        :id, :first_name, :middle_name, :last_name, :sex, :grade,
                        :qualification, :current_position, :gross_salary, :dob, :doe,
                        :nir_number, :county_of_assignment, :department, :category,
                        :created_by, :created_on, :created_at,
                        :trashed_by, :trash_date, :trash_time
                    )
                """), trash_data)

                conn.execute(text("DELETE FROM employee_data WHERE id = :id"), {"id": selected_id})

            st.success("✅ Employee successfully trashed")
        except Exception as e:
            st.error("❌ Error occurred while deleting employee.")
            st.exception(e)
