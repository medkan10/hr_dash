import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
import datetime

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Please login to access this page.")
#     st.stop()
  # Get current user (fallback if not set)

current_user = st.session_state.get("user", {}).get("username", "system")
st.title("🔄 Employee Reclassification")

def run():
    # Fetch all employees for the dropdown
    try:
        employee_df = pd.read_sql("SELECT id, first_name, last_name, department FROM employee_data", get_engine())
        employee_options = employee_df.set_index('id').apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1).tolist()
        employee_ids = employee_df['id'].tolist()
    except Exception as e:
        st.error("⚠️ Could not load employee list. Check your database.")
        st.exception(e)
        st.stop()

    # 🔄 Select employee OUTSIDE the form to trigger rerun
    employee_name = st.selectbox("Select Employee", employee_options)
    selected_employee_id = employee_ids[employee_options.index(employee_name)]

    # Get current position and department
    try:
        employee_data = pd.read_sql(
            f"SELECT current_position, department FROM employee_data WHERE id = {selected_employee_id}",
            get_engine()
        )
        current_position_val = employee_data['current_position'].iloc[0]
        department = employee_data['department'].iloc[0]
    except Exception as e:
        current_position_val = ""
        department = ""
        st.error("⚠️ Could not load current position.")
        st.exception(e)

    # 🧾 Reclassification Form
    with st.form("reclassification_form"):
        current_position = st.text_input("Current Position", value=current_position_val, disabled=True)
        department_from = st.text_input("Department From", value=department, disabled=True)
        department_to = st.text_input("Department To")
        qualification = st.text_input("Qualification")
        reason = st.text_area("Reason for Reclassification")
        new_position = st.text_input("New Position")
        username = current_user

        submitted = st.form_submit_button("Submit Reclassification")

        if submitted:
            if not department_from:
                st.warning("🚫 This employee's initial records have not been updated, please contact an Editor or an Admin")
            elif not department_to or not reason or not new_position:
                st.warning("🚫 Please fill all necessary fields.")
            else:
                now = datetime.datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")
                engine = get_engine()
                with engine.begin() as conn:
                    result = conn.execute(
                        text("SELECT 1 FROM reclassification WHERE id = :id"),
                        {"id": selected_employee_id}
                    ).fetchone()

                    if result:
                        conn.execute(text("""
                            UPDATE reclassification
                            SET current_position = :current_position,
                                department_from = :department_from,
                                department_to = :department_to,
                                qualification = :qualification,
                                reason = :reason,
                                new_position = :new_position,
                                username = :username,
                                date = :date,
                                time = :time
                            WHERE id = :id
                        """), {
                            "id": selected_employee_id,
                            "current_position": current_position_val,
                            "department_from": department,
                            "department_to": department_to,
                            "qualification": qualification,
                            "reason": reason,
                            "new_position": new_position,
                            "username": username,
                            "date": current_date,
                            "time": current_time
                        })
                        st.success(f"🔁 Reclassification for {employee_name} updated successfully.")
                    else:
                        conn.execute(text("""
                            INSERT INTO reclassification (
                                id, current_position, department_from, department_to,
                                qualification, reason, new_position, username, date, time
                            ) VALUES (
                                :id, :current_position, :department_from, :department_to,
                                :qualification, :reason, :new_position, :username, :date, :time
                            )
                        """), {
                            "id": selected_employee_id,
                            "current_position": current_position_val,
                            "department_from": department,
                            "department_to": department_to,
                            "qualification": qualification,
                            "reason": reason,
                            "new_position": new_position,
                            "username": username,
                            "date": current_date,
                            "time": current_time
                        })
                        st.success(f"✅ Reclassification for {employee_name} added successfully.")
    
    # Display reclassification records
    st.markdown("### 📋 All Reclassification Records")
    try:
        df = pd.read_sql("""
            SELECT ed.first_name, ed.last_name, r.current_position, r.department_from, r.department_to,
                   r.qualification, r.reason, r.new_position
            FROM reclassification r
            JOIN employee_data ed ON r.id = ed.id
            ORDER BY r.id DESC
        """, get_engine())
        st.dataframe(df)
    except Exception as e:
        st.error("⚠️ Could not load reclassification records.")
        st.exception(e)
