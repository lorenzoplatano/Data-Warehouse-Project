# src/database/run_olap.py
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from db_config import DATABASE_URL

engine = create_engine(DATABASE_URL)


def load_olap_queries():
    project_root = Path(__file__).resolve().parents[2]
    sql_file = project_root / "sql" / "olap_queries.sql"

    with sql_file.open("r", encoding="utf-8") as file:
        sql_script = file.read()

    return [
        statement.strip()
        for statement in sql_script.split(";")
        if statement.strip()
        and any(line.strip() and not line.strip().startswith("--")
                for line in statement.splitlines())
    ]


def run_queries():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 70)
    print("    RUNNING COMPLETE OLAP QUERIES - MUSEUM DATA WAREHOUSE")
    print("=" * 70)

    queries = load_olap_queries()
    print(f"\n[*] Queries loaded from sql/olap_queries.sql: {len(queries)}")

    for query_number, query in enumerate(queries, start=1):
        print(f"\n--- OLAP Query {query_number} ---")
        result = pd.read_sql(query, engine)
        print(result.to_string(index=False))

    print("\n" + "=" * 70)
    print("All OLAP queries completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    run_queries()