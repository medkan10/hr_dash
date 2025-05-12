import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import text
from db.database import get_engine

st.title("🗃️ Trash Management")

def convert_types(record):
    """Convert numpy types to native Python and handle 'None' strings."""
    safe_record = []
    for val in record:
        if isinstance(val, (np.integer,)):
            val = int(val)
        elif isinstance(val, (np.floating,)):
            val = float(val)
        elif isinstance(val, (np.datetime64, pd.Timestamp)):
            val = str(val.date())  # store as ISO string
        elif val == 'None' or pd.isna(val):
            val = None
        else:
            val = str(val) if val is not None else None
        safe_record.append(val)
    return tuple(safe_record)

def run():
    engine = get_engine()

    try:
        trash_df = pd.read_sql("SELECT * FROM trash ORDER BY trash_date DESC, trash_time DESC", engine)
    except Exception as e:
        st.error("⚠️ Unable to load trash data.")
        st.exception(e)
        st.stop()

    if trash_df.empty:
        st.info("🧹 Trash is empty.")
        st.stop()

    selected_id = st.selectbox(
        "Select a trashed employee to manage",
        trash_df["id"],
        format_func=lambda x: f"{x} - {trash_df[trash_df['id'] == x]['first_name'].values[0]} {trash_df[trash_df['id'] == x]['last_name'].values[0]}"
    )

    record = trash_df[trash_df["id"] == selected_id].iloc[0]
    st.subheader("📋 Trashed Employee Details")
    st.write(record.to_dict())

    action = st.radio("Action", ["Restore Employee", "Permanently Delete"])

    if action == "Restore Employee":
        if st.button("♻️ Confirm Restore"):
            with engine.begin() as conn:
                try:
                    # Convert the record for safe insertion
                    safe_record = convert_types(record.tolist())

                    conn.execute(text("""
                        INSERT INTO employee_data (
                            id, first_name, middle_name, last_name, sex, grade, qualification,
                            current_position, gross_salary, dob, doe, nir_number,
                            county_of_assignment, department, category,
                            created_by, created_on, created_at
                        ) VALUES (
                            :id, :first_name, :middle_name, :last_name, :sex, :grade, :qualification,
                            :current_position, :gross_salary, :dob, :doe, :nir_number,
                            :county_of_assignment, :department, :category,
                            :created_by, :created_on, :created_at
                        )
                    """), dict(zip([
                        "id", "first_name", "middle_name", "last_name", "sex", "grade", "qualification",
                        "current_position", "gross_salary", "dob", "doe", "nir_number",
                        "county_of_assignment", "department", "category",
                        "created_by", "created_on", "created_at"
                    ], safe_record)))

                    conn.execute(text("DELETE FROM trash WHERE id = :id"), {"id": selected_id})
                    st.success("✅ Employee successfully restored.")
                except Exception as e:
                    st.error("❌ Error restoring employee.")
                    st.exception(e)

    elif action == "Permanently Delete":
        if st.button("🗑️ Confirm Permanent Delete"):
            with engine.begin() as conn:
                try:
                    conn.execute(text("DELETE FROM trash WHERE id = :id"), {"id": selected_id})
                    st.success("🧹 Record permanently deleted.")
                except Exception as e:
                    st.error("❌ Error deleting permanently.")
                    st.exception(e)
