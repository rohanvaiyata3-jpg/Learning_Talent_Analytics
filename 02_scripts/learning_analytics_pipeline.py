"""Clean the simulated LMS export and generate a reproducible data-quality report.

Run from any working directory:
    python 02_scripts/learning_analytics_pipeline.py
The script reads 00_raw_data/learning_talent_data.csv and writes the cleaned
dataset and report inside the repository. It never overwrites the raw input.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "00_raw_data" / "learning_talent_data.csv"
CLEAN_DIR = PROJECT_ROOT / "01_clean_data"
DOCS_DIR = PROJECT_ROOT / "07_docs"
CLEAN_PATH = CLEAN_DIR / "learning_talent_clean.csv"
REPORT_PATH = DOCS_DIR / "data_quality_report.txt"

REQUIRED_COLUMNS = {
    "Employee_ID", "Employee_Name", "Department", "Region", "Course_ID",
    "Course_Name", "Course_Category", "Mandatory", "Enrollment_Date",
    "Completion_Date", "Status", "Completion_Rate", "Assessment_Score",
    "Feedback_Rating", "Time_Spent_Hours",
}


def parse_dates(series: pd.Series) -> pd.Series:
    """Parse ISO and day-first dates while safely coercing invalid values."""
    return pd.to_datetime(series, format="mixed", dayfirst=True, errors="coerce")


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_PATH}. "
            "Restore 00_raw_data/learning_talent_data.csv before running."
        )

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW_PATH)
    raw_rows = len(raw)
    missing_columns = REQUIRED_COLUMNS - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Raw dataset is missing required columns: {sorted(missing_columns)}")
    if raw.empty:
        raise ValueError("Raw dataset contains no records.")

    df = raw.copy()

    # Standardize categorical fields before deduplication and analysis.
    for column in ["Department", "Region", "Course_Name", "Course_Category", "Status"]:
        df[column] = df[column].astype("string").str.strip()

    df["Department"] = df["Department"].str.title()
    df["Region"] = df["Region"].str.title().replace(
        {"Us": "US", "Usa": "US", "Uk": "UK", "United States": "US"}
    )
    df["Course_Name"] = df["Course_Name"].str.strip()
    df["Course_Category"] = df["Course_Category"].str.strip()
    df["Status"] = df["Status"].str.title()

    # Normalize Mandatory to a real Boolean; fail loudly on unexpected values.
    mandatory_map = {
        "true": True, "false": False, "yes": True, "no": False,
        "1": True, "0": False,
    }
    df["Mandatory"] = df["Mandatory"].astype("string").str.strip().str.lower().map(mandatory_map)
    if df["Mandatory"].isna().any():
        bad_values = sorted(raw.loc[df["Mandatory"].isna(), "Mandatory"].astype(str).unique())
        raise ValueError(f"Unrecognized Mandatory values: {bad_values}")

    for column in ["Completion_Rate", "Assessment_Score", "Feedback_Rating", "Time_Spent_Hours"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Enrollment_Date"] = parse_dates(df["Enrollment_Date"])
    df["Completion_Date"] = parse_dates(df["Completion_Date"])

    before_deduplication = len(df)
    df = df.drop_duplicates(
        subset=["Employee_ID", "Course_ID", "Enrollment_Date"],
        keep="first",
    ).copy()
    duplicates_removed = before_deduplication - len(df)

    # Capture issue flags before invalid measurements are nulled for analysis.
    df["DQ_Missing_Completion_Date"] = (
        df["Status"].eq("Completed") & df["Completion_Date"].isna()
    )
    df["DQ_Invalid_Score"] = (
        df["Assessment_Score"].notna()
        & ~df["Assessment_Score"].between(0, 100, inclusive="both")
    )
    df["DQ_Invalid_Rating"] = (
        df["Feedback_Rating"].notna()
        & ~df["Feedback_Rating"].between(1, 5, inclusive="both")
    )
    df["DQ_Negative_Hours"] = (
        df["Time_Spent_Hours"].notna() & df["Time_Spent_Hours"].lt(0)
    )

    dq_counts = {
        "Completed records missing completion dates": int(df["DQ_Missing_Completion_Date"].sum()),
        "Invalid assessment scores (outside 0-100)": int(df["DQ_Invalid_Score"].sum()),
        "Invalid feedback ratings (outside 1-5)": int(df["DQ_Invalid_Rating"].sum()),
        "Negative learning-hour values": int(df["DQ_Negative_Hours"].sum()),
    }

    # Keep the exception flags, but exclude invalid numeric values from averages.
    df.loc[df["DQ_Invalid_Score"], "Assessment_Score"] = np.nan
    df.loc[df["DQ_Invalid_Rating"], "Feedback_Rating"] = np.nan
    df.loc[df["DQ_Negative_Hours"], "Time_Spent_Hours"] = np.nan

    df["Days_to_Complete"] = (df["Completion_Date"] - df["Enrollment_Date"]).dt.days
    df["Completion_Bucket"] = pd.cut(
        df["Days_to_Complete"],
        bins=[-1, 30, 60, np.inf],
        labels=["On Time", "Late", "Very Late"],
        include_lowest=True,
    ).astype("string")

    df["Enrollment_Month"] = df["Enrollment_Date"].dt.to_period("M").astype("string")
    df["Enrollment_Quarter"] = df["Enrollment_Date"].dt.to_period("Q").astype("string")
    df["Enrollment_Year"] = df["Enrollment_Date"].dt.year.astype("Int64")
    df["Is_Completed"] = df["Status"].eq("Completed").astype("int64")
    df["Is_Overdue"] = df["Status"].eq("Overdue").astype("int64")

    # Save dates in a consistent ISO format; missing dates remain blank in CSV.
    for column in ["Enrollment_Date", "Completion_Date"]:
        df[column] = df[column].dt.strftime("%Y-%m-%d").fillna("")

    df.to_csv(CLEAN_PATH, index=False)

    department_summary = (
        df.groupby("Department", dropna=False)
        .agg(
            enrollments=("Employee_ID", "size"),
            completions=("Is_Completed", "sum"),
        )
        .reset_index()
    )
    department_summary["completion_rate_pct"] = (
        100 * department_summary["completions"] / department_summary["enrollments"]
    ).round(2)
    department_summary = department_summary.sort_values(
        "completion_rate_pct", ascending=False
    )

    issue_instances = sum(dq_counts.values())
    completed_count = int(df["Is_Completed"].sum())
    completion_rate = round(100 * completed_count / len(df), 2) if len(df) else 0.0
    overdue_count = int(df["Is_Overdue"].sum())
    avg_score = df["Assessment_Score"].mean()
    avg_rating = df["Feedback_Rating"].mean()

    report_lines = [
        "LEARNING & TALENT ANALYTICS - DATA QUALITY REPORT",
        "=" * 58,
        "",
        f"Raw rows loaded: {raw_rows}",
        f"Duplicate rows removed: {duplicates_removed}",
        f"Clean rows written: {len(df)}",
        f"Clean dataset columns: {len(df.columns)}",
        "",
        "DATA QUALITY ISSUE INSTANCES (flags may overlap):",
    ]
    report_lines.extend(f"  - {name}: {count}" for name, count in dq_counts.items())
    report_lines.extend([
        f"  - Total issue instances: {issue_instances}",
        "",
        "KEY METRICS",
        f"  - Completed enrollments: {completed_count}",
        f"  - Completion rate: {completion_rate:.2f}%",
        f"  - Overdue enrollments: {overdue_count}",
        f"  - Average valid assessment score: {avg_score:.2f}" if pd.notna(avg_score) else "  - Average valid assessment score: N/A",
        f"  - Average valid feedback rating: {avg_rating:.3f}" if pd.notna(avg_rating) else "  - Average valid feedback rating: N/A",
        "",
        "COMPLETION RATE BY DEPARTMENT:",
    ])
    for _, row in department_summary.iterrows():
        report_lines.append(
            f"  - {row['Department']}: {row['completion_rate_pct']:.2f}% "
            f"({int(row['completions'])}/{int(row['enrollments'])})"
        )
    report_lines.extend([
        "",
        "Note: The dataset is simulated for portfolio demonstration.",
        "Issue instances count flagged values; one record can have multiple flags.",
        "",
    ])
    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Raw rows loaded: {raw_rows}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Clean rows written: {len(df)}")
    print(f"Data-quality issue instances: {issue_instances}")
    print(f"Completion rate: {completion_rate:.2f}%")
    print(f"Saved cleaned dataset: {CLEAN_PATH}")
    print(f"Saved report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
