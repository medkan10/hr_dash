import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Please login to access this page.")
#     st.stop()

def run():

    st.title("📝 Attendance Module")
    
    # Fetch employees
    try:
        employee_df = pd.read_sql("SELECT id, first_name, last_name FROM employee_data", get_engine())
        employee_options = employee_df.set_index('id').apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1).tolist()
        employee_ids = employee_df['id'].tolist()
    except Exception as e:
        st.error("⚠️ Could not load employee list. Check your database.")
        st.exception(e)
    
    with st.form("attendance_form"):
        employee_name = st.selectbox("Select Employee", employee_options)
        selected_employee_id = employee_ids[employee_options.index(employee_name)]
    
        days_present = st.number_input("Days Present", min_value=0, max_value=31, step=1)
        days_absent = st.number_input("Days Absent", min_value=0, max_value=31, step=1)
        absence_with_excuse = st.number_input("Absence With Excuse", min_value=0, max_value=31, step=1)
        recommended_action = st.selectbox("Recommended Action", ['Regular', 'Salary Deduction', 'Suspension', 'Dismissal'])
        comment = st.text_area("Comment")
    
        submitted = st.form_submit_button("Submit Attendance")
    
        if submitted:
            if days_present + days_absent > 31:
                st.warning("🚫 The sum of Days Present and Days Absent cannot exceed 31.")
            else:
                engine = get_engine()
                with engine.begin() as conn:
                    # Check if a record exists
                    result = conn.execute(
                        text("SELECT 1 FROM attendance WHERE id = :id"),
                        {"id": selected_employee_id}
                    ).fetchone()
    
                    if result:
                        # Update existing attendance
                        conn.execute(text("""
                            UPDATE attendance
                            SET days_present = :days_present,
                                days_absent = :days_absent,
                                absence_with_excuse = :absence_with_excuse,
                                recommended_action = :recommended_action,
                                comment = :comment
                            WHERE id = :id
                        """), {
                            "id": selected_employee_id,
                            "days_present": days_present,
                            "days_absent": days_absent,
                            "absence_with_excuse": absence_with_excuse,
                            "recommended_action": recommended_action,
                            "comment": comment
                        })
                        st.success(f"🔁 Attendance for {employee_name} updated successfully.")
                    else:
                        # Insert new record
                        conn.execute(text("""
                            INSERT INTO attendance (
                                id, days_present, days_absent, absence_with_excuse,
                                recommended_action, comment
                            ) VALUES (
                                :id, :days_present, :days_absent, :absence_with_excuse,
                                :recommended_action, :comment
                            )
                        """), {
                            "id": selected_employee_id,
                            "days_present": days_present,
                            "days_absent": days_absent,
                            "absence_with_excuse": absence_with_excuse,
                            "recommended_action": recommended_action,
                            "comment": comment
                        })
                        st.success(f"✅ Attendance for {employee_name} added successfully.")
    
    # Show all attendance records
    st.markdown("### 📋 All Attendance Records")
    
    try:
        engine = get_engine()
        df = pd.read_sql("""
            SELECT ed.id, ed.first_name, ed.last_name, 
                   a.days_present, a.days_absent, 
                   a.absence_with_excuse, a.recommended_action, a.comment
            FROM attendance a
            JOIN employee_data ed ON a.id = ed.id
            ORDER BY a.id DESC
        """, engine)
    
        for i, row in df.iterrows():
            with st.expander(f"{row['first_name']} {row['last_name']} - Attendance Details"):
                st.write(f"**Days Present:** {row['days_present']}")
                st.write(f"**Days Absent:** {row['days_absent']}")
                st.write(f"**Absence With Excuse:** {row['absence_with_excuse']}")
                st.write(f"**Recommended Action:** {row['recommended_action']}")
                st.write(f"**Comment:** {row['comment']}")
        
                delete_button = st.button("🗑️ Delete Attendance", key=f"delete_{row['id']}_{i}")
        
                if delete_button:
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM attendance WHERE id = :id"), {"id": row['id']})
                    st.success(f"✅ Attendance for {row['first_name']} {row['last_name']} deleted.")
                    st.rerun()
    
    
    except Exception as e:
        st.error("⚠️ Could not load or delete attendance records.")
        st.exception(e)
