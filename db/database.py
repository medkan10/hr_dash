from sqlalchemy import create_engine

# SQLite DB connection
engine = create_engine('sqlite:///hr_dashboard.db')

def get_engine():
    return engine
