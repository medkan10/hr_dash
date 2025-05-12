import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Please login to access this page.")
#     st.stop()

def run():

    st.title("🔄 Employee Reclassification")
    
    # Fetch all employees for the dropdown
    try:
        employee_df = pd.read_sql("SELECT id, first_name, last_name, department FROM employee_data", get_engine())
        employee_options = employee_df.set_index('id').apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1).tolist()
        employee_ids = employee_df['id'].tolist()
    except Exception as e:
        st.error("⚠️ Could not load employee list. Check your database.")
        st.exception(e)
    
    # Reclassification form
    with st.form("reclassification_form"):
        employee_name = st.selectbox("Select Employee", employee_options)
        selected_employee_id = employee_ids[employee_options.index(employee_name)]
    
        try:
            employee_data = pd.read_sql(
                f"SELECT current_position, department FROM employee_data WHERE id = {selected_employee_id}",
                get_engine()
            )
            current_position = employee_data['current_position'].iloc[0]
            department = employee_data['department'].iloc[0]
        except Exception as e:
            current_position = ""
            st.error("⚠️ Could not load current position.")
            st.exception(e)
    
        current_position = st.text_input("Current Position", value=current_position, disabled=True)
        
        department_from = st.text_input("Department From", value=department, disabled=True)
        department_to = st.text_input("Department To")
        qualification = st.text_input("Qualification")
        reason = st.text_area("Reason for Reclassification")
        new_position = st.text_input("New Position")
    
        submitted = st.form_submit_button("Submit Reclassification")
    
        if submitted:
            if not department_from or not department_to or not reason or not new_position:
                st.warning("🚫 Please fill all fields.")
            else:
                engine = get_engine()
                with engine.begin() as conn:
                    # Check if the employee already has a reclassification record
                    result = conn.execute(
                        text("SELECT 1 FROM reclassification WHERE id = :id"),
                        {"id": selected_employee_id}
                    ).fetchone()
    
                    if result:
                        # Update existing record
                        conn.execute(text("""
                            UPDATE reclassification
                            SET current_position = :current_position,
                                department_from = :department_from,
                                department_to = :department_to,
                                qualification = :qualification,
                                reason = :reason,
                                new_position = :new_position
                            WHERE id = :id
                        """), {
                            "id": selected_employee_id,
                            "current_position": current_position,
                            "department_from": department_from,
                            "department_to": department_to,
                            "qualification": qualification,
                            "reason": reason,
                            "new_position": new_position
                        })
                        st.success(f"🔁 Reclassification for {employee_name} updated successfully.")
                    else:
                        # Insert new reclassification record
                        conn.execute(text("""
                            INSERT INTO reclassification (
                                id, current_position, department_from, department_to,
                                qualification, reason, new_position
                            ) VALUES (
                                :id, :current_position, :department_from, :department_to,
                                :qualification, :reason, :new_position
                            )
                        """), {
                            "id": selected_employee_id,
                            "current_position": current_position,
                            "department_from": department_from,
                            "department_to": department_to,
                            "qualification": qualification,
                            "reason": reason,
                            "new_position": new_position
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
