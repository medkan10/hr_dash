import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt
from db.database import get_engine

def run():
    st.title("📊 Employee Data Dashboard")
    
    # Load data
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM employee_data", engine)

    # --- Data Preprocessing ---
    df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
    df['doe'] = pd.to_datetime(df['doe'], errors='coerce')
    df['sex'] = df['sex'].fillna('').str.strip()
    df['verified'] = df['sex'].apply(lambda x: x.lower() in ['male', 'female'])
    df['age'] = df['dob'].apply(lambda x: (datetime.date.today() - x.date()).days // 365 if pd.notnull(x) else None)
    df['pension_eligible'] = df['age'].apply(lambda x: x >= 60 if x is not None else False)

    # --- Metrics ---
    verified_count = df['verified'].sum()
    unverified_count = (~df['verified']).sum()
    avg_salary_verified = df[df['verified']]['gross_salary'].mean()
    avg_salary_unverified = df[~df['verified']]['gross_salary'].mean()
    pension_eligible_count = df['pension_eligible'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("✔️ Verified", verified_count)
    col2.metric("❌ Unverified", unverified_count)
    col3.metric("💰 Avg Salary (Verified)", f"${avg_salary_verified:,.2f}")
    col4.metric("💸 Avg Salary (Unverified)", f"${avg_salary_unverified:,.2f}")
    col5.metric("👵 Pension Eligible", pension_eligible_count)

    # --- Filters ---
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1: sex_filter = st.radio("Sex", options=["All", "Male", "Female"])
    with col2: dept_filter = st.selectbox("Department", options=["All"] + sorted(df['department'].dropna().unique().tolist()))
    with col3: verify_filter = st.radio("Verification Status", options=["All", "Verified", "Unverified"])
    with col4: pension_filter = st.radio("Pension Status", options=["All", "Eligible", "Active"])

    filtered_df = df.copy()

    if sex_filter != "All":
        filtered_df = filtered_df[filtered_df["sex"].str.lower() == sex_filter.lower()]
    if dept_filter != "All":
        filtered_df = filtered_df[filtered_df["department"] == dept_filter]
    if verify_filter != "All":
        is_verified = verify_filter == "Verified"
        filtered_df = filtered_df[filtered_df["verified"] == is_verified]
    if pension_filter != "All":
        is_pension = pension_filter == "Eligible"
        filtered_df = filtered_df[filtered_df["pension_eligible"] == is_pension]

    # --- Charts ---
    col1, col2, col3, col4 = st.columns(4)
    st.subheader("📈 Charts")

    chart1 = alt.Chart(filtered_df.dropna(subset=['doe'])).mark_bar().encode(
        x=alt.X("year(doe):O", title="Employment Year"),
        y=alt.Y("count():Q", title="Employees")
    ).properties(title="Trend of Employment by Year", width=600)


    chart2 = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X("department:N", sort='-y'),
        y="count():Q",
        tooltip=["department", "count()"]
    ).properties(title="Employee Count by Department", width=600).interactive()

    chart3 = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X("qualification:N", sort='-y'),
        y="count():Q",
        tooltip=["qualification", "count()"]
    ).properties(title="Employee Count by Qualification", width=600).interactive()
    
    pension_data = pd.DataFrame({
        "Status": ["Eligible", "Active"],
        "Count": [
            filtered_df['pension_eligible'].sum(),
            (~filtered_df['pension_eligible']).sum()
        ]
    })

    pie_chart = alt.Chart(pension_data).mark_arc().encode(
        theta="Count:Q",
        color="Status:N"
    ).properties(title="Pension Status Distribution", width=400)
    
    col1, col2 = st.columns(2)
    with col1: st.altair_chart(chart1)
    with col2: st.altair_chart(chart2)

    col1, col2 = st.columns(2)
    with col1: st.altair_chart(chart3)
    with col2: st.altair_chart(pie_chart)

    # --- Filtered Table ---
    st.subheader("📋 Filtered Employee Data")
    st.dataframe(filtered_df)

