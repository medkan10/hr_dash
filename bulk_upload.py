import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.database import get_engine
from datetime import datetime

st.title("📦 Bulk Upload Employees")

# Get current user (fallback if not set)
current_user = st.session_state.get("user", {}).get("username", "system")

def run():
    # 1. Upload Excel file
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            # 2. Read data into DataFrame
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("📊 Preview of Uploaded Data")
            st.dataframe(df)

            # Optional: Validate column names
            required_columns = {"first_name", "middle_name", "last_name", "nir_number", "current_position", "gross_salary", "category"}
            if not required_columns.issubset(df.columns):
                st.warning(f"⚠️ Missing required columns. Ensure your file includes: {', '.join(required_columns)}")
            else:
                if st.button("🚀 Upload to Database"):
                    created_on = datetime.today().date()
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    engine = get_engine()
                    with engine.begin() as conn:
                        for _, row in df.iterrows():
                            conn.execute(text("""
                                INSERT INTO employee_data (first_name, middle_name, last_name, nir_number, current_position, gross_salary, category, created_by, created_on, created_at)
                                VALUES (:first_name, :middle_name, :last_name, :nir_number, :current_position, :gross_salary, :category, :created_by, :created_on, :created_at)
                            """), {
                                "first_name": row["first_name"],
                                "middle_name": row["middle_name"],
                                "last_name": row["last_name"],
                                "nir_number": row["nir_number"],
                                "current_position": row["current_position"],
                                "gross_salary": row["gross_salary"],
                                "category": row["category"],
                                "created_by":current_user,
                                "created_on": created_on,
                                "created_at": created_at
                            })
                    st.success("✅ Employees uploaded successfully!")
        except Exception as e:
            st.error("❌ Error reading or uploading the file.")
            st.exception(e)
