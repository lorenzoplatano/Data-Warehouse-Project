# Data-Warehouse-Project

## Database connection

The database scripts (`init_db.py`, `load_dw.py`, and `run_olap.py`) share their
connection settings from `src/database/db_config.py`. Set these environment
variables before running a script to override the defaults:

| Variable | Default |
| --- | --- |
| `DB_NAME` | `museum_dw` |
| `DB_USER` | `postgres` |
| `DB_PASS` | empty |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |

For example, in PowerShell:

```powershell
$env:DB_PASS = "your-local-database-password"
python .\src\database\init_db.py
```

Set `DB_PASS` in your environment rather than committing credentials to the
repository.