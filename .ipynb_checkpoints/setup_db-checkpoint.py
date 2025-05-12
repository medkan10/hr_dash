from db.database import get_engine
from sqlalchemy import text

# Read the full SQL schema as one string
with open("db/schema.sql", "r") as f:
    schema_sql = f.read()

# Split the string into individual statements
statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]

engine = get_engine()

# Execute each statement separately
with engine.connect() as conn:
    for statement in statements:
        conn.execute(text(statement))
    print("✅ Database initialized successfully.")
