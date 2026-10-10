
import pandas as pd
from sqlalchemy import create_engine
import sys

sys.stdout.reconfigure(encoding='utf-8')

MYSQL_USER = "root"
MYSQL_PASSWORD = "Rohan8850"   
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "learning_talent_db"

CSV_PATH = r"C:\Users\Rohan Vaiyata\OneDrive\Desktop\1_Project\3_Learning & Talent Analytics\01_clean_data\learning_talent_clean.csv"

# Read CSV
print(f"Reading: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")

# Sanity check: duplicate column names?
dupes = [c for c in df.columns if list(df.columns).count(c) > 1]
if dupes:
    print(f"  WARNING: Duplicate columns found: {set(dupes)}")
    df = df.loc[:, ~df.columns.duplicated()]
    print(f"   Removed duplicates → {len(df.columns)} columns remain")

for col in df.columns:
    if df[col].dtype == 'bool':
        df[col] = df[col].astype(int)

df = df.where(pd.notna(df), None)

connection_str = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
print(f"\nConnecting to MySQL...")
engine = create_engine(connection_str)

table_name = "learning_talent"
print(f"Pushing to table `{table_name}`...")

df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"\n Pushed {len(df)} rows to `{MYSQL_DB}.{table_name}`")

result = pd.read_sql(f"SELECT COUNT(*) AS row_count FROM {table_name}", engine)
print(f" Verified in MySQL: {result['row_count'].iloc[0]} rows")

print(f"\nSample data from MySQL:")
sample = pd.read_sql(f"SELECT Employee_ID, Department, Region, Course_Name, Status FROM {table_name} LIMIT 5", engine)
print(sample.to_string(index=False))