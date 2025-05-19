from sqlalchemy import text
from db.database import get_engine

def run():
    engine = get_engine()
    with engine.begin() as conn:
        # Disable FK checks (if using SQLite) - optional
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Delete dependent records first
        conn.execute(text("DELETE FROM attendance"))
        conn.execute(text("DELETE FROM reclassification"))
        # Add more as needed

        # Then delete from employee_data
        conn.execute(text("DELETE FROM employee_data"))

        # Re-enable FK checks
        conn.execute(text("PRAGMA foreign_keys = ON"))
