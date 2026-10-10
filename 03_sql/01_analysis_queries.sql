-- Learning & Talent Analytics
-- Database: MySQL 8.0+
-- Load the cleaned CSV into learning_talent_db.learning_talent first.
-- Mandatory is stored as 1 = mandatory, 0 = optional.

USE learning_talent_db;

-- 1. Dataset size and distinct entities
SELECT
    COUNT(*) AS total_enrollments,
    COUNT(DISTINCT Employee_ID) AS unique_employees,
    COUNT(DISTINCT Course_ID) AS unique_courses,
    COUNT(DISTINCT Department) AS departments,
    COUNT(DISTINCT Region) AS regions
FROM learning_talent;

-- 2. Check duplicate business keys. Multiple courses per employee are valid;
-- a duplicate is defined by employee + course + enrollment date.
SELECT Employee_ID, Course_ID, Enrollment_Date, COUNT(*) AS duplicate_count
FROM learning_talent
GROUP BY Employee_ID, Course_ID, Enrollment_Date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 3. Data-quality summary using flags created by the Python pipeline.
SELECT
    COUNT(*) AS clean_table_rows,
    SUM(CASE WHEN DQ_Missing_Completion_Date = 1 THEN 1 ELSE 0 END)
        AS completed_records_missing_completion_date,
    SUM(CASE WHEN DQ_Invalid_Score = 1 THEN 1 ELSE 0 END)
        AS invalid_score_instances,
    SUM(CASE WHEN DQ_Invalid_Rating = 1 THEN 1 ELSE 0 END)
        AS invalid_rating_instances,
    SUM(CASE WHEN DQ_Negative_Hours = 1 THEN 1 ELSE 0 END)
        AS negative_learning_hour_instances,
    SUM(CASE WHEN DQ_Missing_Completion_Date = 1
               OR DQ_Invalid_Score = 1
               OR DQ_Invalid_Rating = 1
               OR DQ_Negative_Hours = 1
             THEN 1 ELSE 0 END) AS rows_with_at_least_one_flag
FROM learning_talent;

-- 4. Executive KPI summary
SELECT
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completed_enrollments,
    SUM(Is_Overdue) AS overdue_enrollments,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_valid_assessment_score,
    ROUND(AVG(Feedback_Rating), 3) AS avg_valid_feedback_rating,
    ROUND(AVG(Time_Spent_Hours), 2) AS avg_valid_learning_hours
FROM learning_talent;

-- 5. Enrollment status mix
SELECT
    Status,
    COUNT(*) AS enrollments,
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM learning_talent), 0), 2)
        AS share_of_enrollments_pct
FROM learning_talent
GROUP BY Status
ORDER BY enrollments DESC;

-- 6. Completion by department
SELECT
    Department,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    SUM(Is_Overdue) AS overdue_enrollments,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 3) AS avg_rating
FROM learning_talent
GROUP BY Department
ORDER BY completion_rate_pct DESC;

-- 7. Status mix by department
SELECT Department, Status, COUNT(*) AS enrollments
FROM learning_talent
GROUP BY Department, Status
ORDER BY Department, enrollments DESC;

-- 8. Completion by region
SELECT
    Region,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    SUM(Is_Overdue) AS overdue_enrollments
FROM learning_talent
GROUP BY Region
ORDER BY completion_rate_pct DESC;

-- 9. Mandatory versus optional training (Mandatory: 1 = yes, 0 = no)
SELECT
    Mandatory,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    SUM(Is_Overdue) AS overdue_enrollments
FROM learning_talent
GROUP BY Mandatory
ORDER BY Mandatory DESC;

-- 10. Mandatory overdue enrollments by department
SELECT Department, COUNT(*) AS overdue_mandatory_enrollments
FROM learning_talent
WHERE Mandatory = 1 AND Is_Overdue = 1
GROUP BY Department
ORDER BY overdue_mandatory_enrollments DESC;

-- 11. Course-level performance
SELECT
    Course_ID,
    Course_Name,
    Course_Category,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 3) AS avg_rating
FROM learning_talent
GROUP BY Course_ID, Course_Name, Course_Category
ORDER BY completion_rate_pct DESC, enrollments DESC;

-- 12. Courses with completion rates below 60%
SELECT
    Course_ID,
    Course_Name,
    COUNT(*) AS enrollments,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct
FROM learning_talent
GROUP BY Course_ID, Course_Name
HAVING 100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0) < 60
ORDER BY completion_rate_pct ASC;

-- 13. Performance by course category
SELECT
    Course_Category,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 3) AS avg_rating
FROM learning_talent
GROUP BY Course_Category
ORDER BY completion_rate_pct DESC;

-- 14. Average time to completion by course category (completed records only)
SELECT
    Course_Category,
    ROUND(AVG(CASE WHEN Is_Completed = 1 THEN Days_to_Complete END), 2)
        AS avg_days_to_complete
FROM learning_talent
GROUP BY Course_Category
ORDER BY avg_days_to_complete;

-- 15. Monthly enrollment and completion trend
SELECT
    Enrollment_Month,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score
FROM learning_talent
GROUP BY Enrollment_Month
ORDER BY Enrollment_Month;

-- 16. Quarterly enrollment and completion trend
SELECT
    Enrollment_Year,
    Enrollment_Quarter,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct
FROM learning_talent
GROUP BY Enrollment_Year, Enrollment_Quarter
ORDER BY Enrollment_Year, Enrollment_Quarter;

-- 17. Completion duration buckets
SELECT Completion_Bucket, COUNT(*) AS records
FROM learning_talent
WHERE Is_Completed = 1
GROUP BY Completion_Bucket
ORDER BY records DESC;

-- 18. Course completion ranking (MySQL 8.0+)
WITH course_performance AS (
    SELECT
        Course_ID,
        Course_Name,
        COUNT(*) AS enrollments,
        ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct
    FROM learning_talent
    GROUP BY Course_ID, Course_Name
)
SELECT
    Course_ID,
    Course_Name,
    enrollments,
    completion_rate_pct,
    RANK() OVER (ORDER BY completion_rate_pct DESC) AS completion_rank
FROM course_performance
ORDER BY completion_rank, Course_Name;

-- 19. Department completion ranking (MySQL 8.0+)
WITH department_performance AS (
    SELECT
        Department,
        COUNT(*) AS enrollments,
        ROUND(100.0 * SUM(Is_Completed) / NULLIF(COUNT(*), 0), 2) AS completion_rate_pct
    FROM learning_talent
    GROUP BY Department
)
SELECT
    Department,
    enrollments,
    completion_rate_pct,
    DENSE_RANK() OVER (ORDER BY completion_rate_pct DESC) AS department_rank
FROM department_performance
ORDER BY department_rank, Department;

-- 20. Missingness after cleaning. Some missing values are expected for incomplete
-- enrollments; use the DQ flags above to distinguish identified source issues.
SELECT
    SUM(CASE WHEN Assessment_Score IS NULL THEN 1 ELSE 0 END) AS missing_scores,
    SUM(CASE WHEN Feedback_Rating IS NULL THEN 1 ELSE 0 END) AS missing_ratings,
    SUM(CASE WHEN Completion_Date IS NULL OR Completion_Date = '' THEN 1 ELSE 0 END)
        AS missing_completion_dates,
    SUM(CASE WHEN Days_to_Complete IS NULL THEN 1 ELSE 0 END) AS missing_days_to_complete
FROM learning_talent;
