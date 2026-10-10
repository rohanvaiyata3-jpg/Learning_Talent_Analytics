# Learning & Talent Analytics

An end-to-end data analytics portfolio project that transforms raw employee learning and training data into actionable business insights using Python, MySQL, and Tableau.

![Project Status](https://img.shields.io/badge/status-complete-brightgreen)
![Tools](https://img.shields.io/badge/tools-Python%20%7C%20MySQL%20%7C%20Tableau-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Project Overview

Organizations invest heavily in employee training but often lack visibility into **participation, completion, and course effectiveness**. Raw learning data also frequently contains quality issues - missing dates, invalid scores, negative hours - that distort reporting.

This project demonstrates a complete analytics workflow:

- **Data cleaning and validation** in Python
- **Structured storage and analysis** in MySQL
- **Interactive dashboards** in Tableau
- **Business recommendations** based on the findings

---

## Business Objective

Turn raw training data into a clear, decision-ready view of learning performance by answering three questions:

1. Are employees **participating** in training?
2. Are they **completing** it?
3. Is the training actually **effective**?

---

## Tools Used

| Tool | Purpose |
|------|---------|
| **Python** | Data cleaning, validation, quality exception logging |
| **MySQL** | Structured storage + SQL analysis queries |
| **Tableau** | 4 interactive dashboards with filters |
| **Git / GitHub** | Version control and portfolio hosting |

**Python libraries:** `pandas`, `numpy`, `mysql-connector-python`

---

## Dataset Overview

| Metric | Value |
|--------|-------|
| Raw dataset rows | 1,030 |
| Cleaned dataset rows | 1,002 |
| Columns | 26 |
| Rows removed during cleaning | 28 |
| Data-quality exceptions logged | 37 |

### Data Quality Exceptions

| Exception Type | Count |
|----------------|-------|
| Missing completion dates | 25 |
| Invalid scores | 5 |
| Invalid ratings | 3 |
| Negative learning hours | 4 |
| **Total** | **37** |

> **Note:** 28 rows were removed from the raw dataset, while **37 data-quality exceptions** were recorded. These figures measure different things - a single record could contain more than one issue.

---

## Key Findings (KPIs)

| KPI | Value |
|-----|-------|
| Total Enrollments | **1,002** |
| Completion Rate | **67.2%** |
| Average Assessment Score | **80.95** |
| Average Feedback Rating | **4.006 / 5** |
| Overdue Records | **100** |

**Insight:** When learners complete training, they rate it highly (4.0/5). The bigger opportunity is improving completion - roughly **1 in 3 enrollments is not completed**.

---

## Tableau Dashboards

The project includes four interactive dashboards:

### 1. Executive Summary
High-level KPIs and monthly completion trend.
- 5 KPI cards (Enrollments, Completion Rate, Avg Score, Avg Rating, Overdue)
- Monthly completion trend line
- Completion by department bar chart
- **Filters:** Region, Course Category, Mandatory

### 2. Participation & Completion
Learner engagement and completion patterns.
- Enrollment breakdown by region and department
- Completion rates and incomplete training
- Departmental and category-level comparisons

### 3. Course Performance
Course effectiveness and learner outcomes.
- Assessment scores by course
- Learner feedback and ratings
- Comparison across categories

### 4. Data Quality & Exceptions
Data problems that can affect reporting reliability.
- Missing completion dates: 25
- Invalid scores: 5
- Invalid ratings: 3
- Negative learning hours: 4
- **Total recorded exceptions: 37**

---

## Repository Structure

```
Learning_Talent_Analytics/
│
├── 00_raw_data/
│   └── learning_talent_data.csv
│
├── 01_clean_data/
│   └── learning_talent_clean.csv
│
├── 02_scripts/
│   ├── learning_analytics_pipeline.py
│   └── push_to_mysql.py
│
├── 03_sql/
│   └── 01_analysis_queries.sql
│
├── 04_tableau/
│   └── Learning_Talent_Analytics.twbx
│
├── 05_powerpoint/
│   └── Learning_Talent_Analytics.pptx
│
├── 06_screenshots/
│   ├── 1_Learning_and_talent.png
│   ├── 2_Participation_and_completion.png
│   ├── 3_Course_performance.png
│   └── 4_Data_quality_and_exceptions.png
│
├── 07_docs/
│   └── data_quality_report.txt
│
└── README.md
```

---

## Methodology

1. **Data ingestion** - Raw CSV (1,030 rows × 26 columns) loaded into Python
2. **Data cleaning** - Missing values handled, invalid entries corrected, negative hours flagged
3. **Quality logging** - 37 exceptions recorded across 4 categories
4. **Storage** - Cleaned dataset pushed to MySQL
5. **SQL analysis** - Aggregations, joins, and KPI calculations
6. **Dashboarding** - 4 Tableau dashboards with filters for Region, Course Category, and Mandatory
7. **Reporting** - Findings documented in PowerPoint and this README

---

## Dashboard Screenshots

### Executive Summary
![Executive Summary](06_screenshots/1_Learning_&_talent.png)

### Participation & Completion
![Participation & Completion](06_screenshots/2_Participation_&_completion.png)

### Course Performance
![Course Performance](06_screenshots/3_Course_performance.png)

### Data Quality & Exceptions
![Data Quality & Exceptions](06_screenshots/4_Data_quality_&_exceptions.png)

---

## Recommendations

1. **Target the 100 overdue records** with automated reminders - quick win for completion rate.
2. **Investigate low-completion departments** surfaced in the Participation dashboard.
3. **Fix the data pipeline** - 25 missing completion dates undermine completion reporting.
4. **Use high-rated courses as templates** for underperforming ones.

### Next Steps
- Connect live LMS data for automated refresh
- Add a predictive model for completion likelihood
- Publish dashboards to Tableau Public / internal server

---

## How to Use This Project

### 1. Clone the repository
```bash
git clone https://github.com/rohanvaiyata3-jpg/Learning_Talent_Analytics.git
cd Learning_Talent_Analytics
```

### 2. Run the Python pipeline
```bash
pip install pandas numpy mysql-connector-python
python 02_scripts/learning_analytics_pipeline.py
```

### 3. Load into MySQL 
```bash
python 02_scripts/push_to_mysql.py
```

### 4. Run SQL analysis
Open `03_sql/01_analysis_queries.sql` in MySQL Workbench or any SQL client.

### 5. Open the Tableau workbook
Open `04_tableau/Learning_Talent_Analytics.twbx` in Tableau Desktop or Tableau Reader.

### 6. Review the presentation
Open `05_powerpoint/Learning_Talent_Analytics.pptx` for the 7-slide project summary.

---

## Author

**Rohan Vaiyata**
- GitHub: [@rohanvaiyata3-jpg](https://github.com/rohanvaiyata3-jpg)
- LinkedIn: [rohan-vaiyata](https://www.linkedin.com/in/rohan-vaiyata/)
- Email: rohanvaiyata3@gmail.com

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- Dataset: Simulated learning management system (LMS) export
- Tools: Python, MySQL, Tableau
