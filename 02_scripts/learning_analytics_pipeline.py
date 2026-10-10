import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')


PROJECT_FOLDER = r"C:\Users\Rohan Vaiyata\OneDrive\Desktop\1_Project\3_Learning & Talent Analytics"
RAW_FOLDER = os.path.join(PROJECT_FOLDER, "00_raw_data")
CLEAN_FOLDER = os.path.join(PROJECT_FOLDER, "01_clean_data")
DOCS_FOLDER = os.path.join(PROJECT_FOLDER, "07_docs")

os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)
os.makedirs(DOCS_FOLDER, exist_ok=True)

print(f"Project folder: {PROJECT_FOLDER}")
print(f"Raw data folder: {RAW_FOLDER}")
print(f"Clean data folder: {CLEAN_FOLDER}")
print(f"Docs folder: {DOCS_FOLDER}\n")


print("=" * 60)
print("PART 1: Generating raw dataset")
print("=" * 60)

np.random.seed(42)
random.seed(42)

n = 1000

departments = ['Tax', 'Legal', 'Audit', 'Consulting', 'Finance', 'Advisory']
regions = ['India', 'US', 'UK', 'Singapore', 'Australia', 'Germany']
courses = [
    ('CRS001', 'Data Privacy Fundamentals', 'Compliance', True),
    ('CRS002', 'Power BI Essentials', 'Technical', False),
    ('CRS003', 'Leadership 101', 'Leadership', False),
    ('CRS004', 'Cyber Security Awareness', 'Compliance', True),
    ('CRS005', 'Advanced Excel', 'Technical', False),
    ('CRS006', 'Anti-Bribery & Corruption', 'Compliance', True),
    ('CRS007', 'Tableau for Analysts', 'Technical', False),
    ('CRS008', 'Effective Communication', 'Leadership', False),
    ('CRS009', 'AI & Ethics', 'Digital Learning', False),
    ('CRS010', 'Code of Conduct', 'Compliance', True),
    ('CRS011', 'SQL Fundamentals', 'Technical', False),
    ('CRS012', 'Emotional Intelligence', 'Leadership', False),
    ('CRS013', 'Digital Learning Design', 'Digital Learning', False),
    ('CRS014', 'Data Storytelling', 'Digital Learning', False),
    ('CRS015', 'Time Management', 'Leadership', False),
]
statuses = ['Completed', 'In Progress', 'Not Started', 'Overdue']
status_weights = [0.65, 0.15, 0.10, 0.10]

rows = []
for i in range(n):
    emp_id = f"EMP{random.randint(1, 300):03d}"
    course_id, course_name, category, mandatory = random.choice(courses)
    dept = random.choice(departments)
    region = random.choice(regions)

    enroll_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))
    status = np.random.choice(statuses, p=status_weights)

    if status == 'Completed':
        completion_date = enroll_date + timedelta(days=random.randint(1, 60))
        completion_rate = 100
        score = random.randint(60, 100)
        feedback = round(random.uniform(3.0, 5.0), 1)
        hours = round(random.uniform(1.0, 10.0), 1)
    elif status == 'In Progress':
        completion_date = None
        completion_rate = random.choice([25, 50, 75])
        score = None
        feedback = None
        hours = round(random.uniform(0.5, 5.0), 1)
    elif status == 'Overdue':
        completion_date = None
        completion_rate = random.choice([0, 25, 50])
        score = None
        feedback = None
        hours = round(random.uniform(0.0, 2.0), 1)
    else:
        completion_date = None
        completion_rate = 0
        score = None
        feedback = None
        hours = 0.0

    rows.append({
        'Employee_ID': emp_id,
        'Employee_Name': f"Employee_{i+1}",
        'Department': dept,
        'Region': region,
        'Course_ID': course_id,
        'Course_Name': course_name,
        'Course_Category': category,
        'Mandatory': mandatory,
        'Enrollment_Date': enroll_date.strftime('%Y-%m-%d'),
        'Completion_Date': completion_date.strftime('%Y-%m-%d') if completion_date else '',
        'Status': status,
        'Completion_Rate': completion_rate,
        'Assessment_Score': score,
        'Feedback_Rating': feedback,
        'Time_Spent_Hours': hours
    })

df = pd.DataFrame(rows)

# Deliberate messiness
duplicates = df.sample(30, random_state=1)
df = pd.concat([df, duplicates], ignore_index=True)

df.loc[df.sample(20, random_state=2).index, 'Department'] = 'tax'
df.loc[df.sample(15, random_state=3).index, 'Department'] = 'LEGAL'
df.loc[df.sample(10, random_state=4).index, 'Region'] = 'india'
df.loc[df.sample(8, random_state=5).index, 'Region'] = 'USA'

completed_idx = df[df['Status'] == 'Completed'].sample(25, random_state=6).index
df.loc[completed_idx, 'Completion_Date'] = ''

df.loc[df.sample(5, random_state=7).index, 'Assessment_Score'] = 105
df.loc[df.sample(3, random_state=8).index, 'Feedback_Rating'] = 6.5
df.loc[df.sample(4, random_state=9).index, 'Time_Spent_Hours'] = -2.0

df.loc[df.sample(10, random_state=10).index, 'Enrollment_Date'] = '15/03/2025'

raw_path = os.path.join(RAW_FOLDER, 'learning_talent_data.csv')
df.to_csv(raw_path, index=False)
print(f"   Saved: {raw_path}")
print(f"   Rows: {len(df)}")


print("\n" + "=" * 60)
print("PART 2: Cleaning dataset")
print("=" * 60)

df = pd.read_csv(raw_path)
print(f"Loaded {len(df)} rows")

df['Department'] = df['Department'].str.strip().str.title()
df['Region'] = df['Region'].str.strip().str.title()
df['Region'] = df['Region'].replace({'Usa': 'US', 'Uk': 'UK'})
df['Course_Name'] = df['Course_Name'].str.strip()
df['Course_Category'] = df['Course_Category'].str.strip()
print("Standardized Department & Region names")

df['Enrollment_Date'] = pd.to_datetime(
    df['Enrollment_Date'], format='mixed', dayfirst=True, errors='coerce'
)
df['Completion_Date'] = pd.to_datetime(
    df['Completion_Date'], format='mixed', dayfirst=True, errors='coerce'
)
print("Parsed dates")

before = len(df)
df = df.drop_duplicates(subset=['Employee_ID', 'Course_ID', 'Enrollment_Date'])
removed = before - len(df)
print(f"Removed {removed} duplicate rows -> {len(df)} rows remain")

df['DQ_Missing_Completion_Date'] = (df['Status'] == 'Completed') & (df['Completion_Date'].isna())
df['DQ_Invalid_Score'] = df['Assessment_Score'] > 100
df['DQ_Invalid_Rating'] = (df['Feedback_Rating'] < 1) | (df['Feedback_Rating'] > 5)
df['DQ_Negative_Hours'] = df['Time_Spent_Hours'] < 0

dq_summary = {
    'Missing completion dates': int(df['DQ_Missing_Completion_Date'].sum()),
    'Invalid scores (>100)': int(df['DQ_Invalid_Score'].sum()),
    'Invalid ratings (outside 1-5)': int(df['DQ_Invalid_Rating'].sum()),
    'Negative time spent': int(df['DQ_Negative_Hours'].sum()),
}
print("\nData Quality Issues Found:")
for k, v in dq_summary.items():
    print(f"  - {k}: {v}")

df.loc[df['DQ_Invalid_Score'], 'Assessment_Score'] = np.nan
df.loc[df['DQ_Invalid_Rating'], 'Feedback_Rating'] = np.nan
df.loc[df['DQ_Negative_Hours'], 'Time_Spent_Hours'] = np.nan

df['Days_to_Complete'] = (df['Completion_Date'] - df['Enrollment_Date']).dt.days
df['Completion_Bucket'] = pd.cut(
    df['Days_to_Complete'],
    bins=[-1, 30, 60, 999],
    labels=['On Time', 'Late', 'Very Late']
)
df['Enrollment_Month'] = df['Enrollment_Date'].dt.to_period('M').astype(str)
df['Enrollment_Quarter'] = df['Enrollment_Date'].dt.to_period('Q').astype(str)
df['Enrollment_Year'] = df['Enrollment_Date'].dt.year
df['Is_Completed'] = (df['Status'] == 'Completed').astype(int)
df['Is_Overdue'] = (df['Status'] == 'Overdue').astype(int)
print("Derived new columns")

df['Enrollment_Date'] = df['Enrollment_Date'].dt.strftime('%Y-%m-%d')
df['Completion_Date'] = df['Completion_Date'].dt.strftime('%Y-%m-%d')
df['Completion_Date'] = df['Completion_Date'].fillna('')
df['Completion_Bucket'] = df['Completion_Bucket'].astype(str).replace('nan', '')

clean_path = os.path.join(CLEAN_FOLDER, 'learning_talent_clean.csv')
df.to_csv(clean_path, index=False)
print(f"\n Saved: {clean_path} ({len(df)} rows)")

print("\n" + "=" * 60)
print("PART 3: Data Quality Report")
print("=" * 60)

dept_summary = df.groupby('Department').agg(
    enrollments=('Employee_ID', 'count'),
    completions=('Is_Completed', 'sum')
).reset_index()
dept_summary['completion_rate_pct'] = (
    100 * dept_summary['completions'] / dept_summary['enrollments']
).round(2)
dept_summary = dept_summary.sort_values('completion_rate_pct', ascending=False)

print("\nCompletion Rate by Department:")
print(dept_summary.to_string(index=False))

report_path = os.path.join(DOCS_FOLDER, 'data_quality_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("LEARNING & TALENT ANALYTICS - DATA QUALITY REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Raw rows: {before + removed}\n")
    f.write(f"Duplicates removed: {removed}\n")
    f.write(f"Final rows: {len(df)}\n\n")
    f.write("DQ ISSUES FOUND:\n")
    for k, v in dq_summary.items():
        f.write(f"  - {k}: {v}\n")
    f.write("\nCOMPLETION RATE BY DEPARTMENT:\n")
    for _, r in dept_summary.iterrows():
        f.write(f"  {r['Department']}: {r['completion_rate_pct']}% "
                f"({r['completions']}/{r['enrollments']})\n")

print(f"\nSaved: {report_path}")
print("\n" + "=" * 60)
print("PHASE 1 COMPLETE")
print("=" * 60)