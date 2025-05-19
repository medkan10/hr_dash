# backup.py

import streamlit as st
import os
import shutil
from datetime import datetime


def run():
    st.title("📦 Backup Database")

    db_path = "hr_dashboard.db"
    backup_dir = "backups"

    def backup_database():
        if not os.path.exists(db_path):
            st.error(f"Database file '{db_path}' not found.")
            return

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"hr_dashboard_backup_{timestamp}.db")

        try:
            shutil.copy2(db_path, backup_file)
            st.success(f"✅ Backup created successfully: `{backup_file}`")
        except Exception as e:
            st.error("❌ Failed to back up database.")
            st.exception(e)

    if st.button("📁 Backup Now"):
        backup_database()
