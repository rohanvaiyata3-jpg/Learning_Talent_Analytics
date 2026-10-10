import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

sys.stdout.reconfigure(encoding="utf-8")

# Load local settings from .env when present. Never commit the actual .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "learning_talent_db")

CSV_PATH = PROJECT_ROOT / "01_clean_data" / "learning_talent_clean.csv"

if not MYSQL_PASSWORD:
    raise SystemExit(
        "Missing MYSQL_PASSWORD. Create a local .env file from .env.example "
        "and set your MySQL credentials."
    )

if not CSV_PATH.exists():
    raise SystemExit(
        f"Clean dataset not found: {CSV_PATH}\n"
        "Run 02_scripts/learning_analytics_pipeline.py first."
    )

print(f"Reading: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

# Guard against duplicate column names before writing to MySQL.
if df.columns.duplicated().any():
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    print(f"WARNING: Duplicate columns found: {duplicate_columns}")
    df = df.loc[:, ~df.columns.duplicated()]
    print(f"Removed duplicate columns; {len(df.columns)} columns remain")

# Convert Boolean columns to integers for predictable MySQL storage.
for column in df.columns:
    if pd.api.types.is_bool_dtype(df[column]):
        df[column] = df[column].astype("int64")

# Convert pandas missing values to Python None for SQL insertion.
df = df.astype(object).where(pd.notna(df), None)

connection_url = URL.create(
    drivername="mysql+mysqlconnector",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DB,
)

print("\nConnecting to MySQL...")
engine = create_engine(connection_url)

table_name = "learning_talent"
print(f"Pushing to table `{table_name}`...")
df.to_sql(table_name, engine, if_exists="replace", index=False)

print(f"\nPushed {len(df)} rows to `{MYSQL_DB}.{table_name}`")

result = pd.read_sql(f"SELECT COUNT(*) AS row_count FROM `{table_name}`", engine)
verified_rows = int(result["row_count"].iloc[0])
print(f"Verified in MySQL: {verified_rows} rows")

if verified_rows != len(df):
    raise RuntimeError(
        f"Row-count mismatch: DataFrame has {len(df)} rows, "
        f"but MySQL contains {verified_rows} rows."
    )

sample = pd.read_sql(
    f"SELECT Employee_ID, Department, Region, Course_Name, Status "
    f"FROM `{table_name}` LIMIT 5",
    engine,
)
print("\nSample data from MySQL:")
print(sample.to_string(index=False))
engine.dispose()
