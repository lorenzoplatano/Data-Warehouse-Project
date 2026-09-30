from pathlib import Path
from sqlalchemy import create_engine, text
from db_config import DATABASE_URL

engine = create_engine(DATABASE_URL)

def create_tables():
    # Resolve the absolute path to sql/ regardless of where the script is run
    project_root = Path(__file__).resolve().parents[2]
    sql_file = project_root / "sql" / "create_schema.sql"

    print(f"Reading SQL script from: {sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    try:
        with engine.begin() as conn:
            conn.execute(text(sql_commands))
            print("Tables and sentinel records successfully created in museum_dw!")
    except Exception as e:
        print(f"Error while executing the script: {e}")

if __name__ == "__main__":
    create_tables()