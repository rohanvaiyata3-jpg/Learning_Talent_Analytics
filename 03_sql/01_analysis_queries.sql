
USE learning_talent_db;

SELECT COUNT(*) AS total_rows FROM learning_talent;

SELECT Employee_ID, Course_ID, COUNT(*) AS enrollment_count
FROM learning_talent
GROUP BY Employee_ID, Course_ID
HAVING COUNT(*) > 1
ORDER BY enrollment_count DESC;

SELECT COUNT(*) AS missing_completion_dates
FROM learning_talent
WHERE Status = 'Completed' AND Completion_Date IS NULL;

SELECT COUNT(*) AS invalid_scores
FROM learning_talent
WHERE Assessment_Score < 0 OR Assessment_Score > 100;

SELECT COUNT(*) AS invalid_ratings
FROM learning_talent
WHERE Feedback_Rating < 1 OR Feedback_Rating > 5;

SELECT COUNT(*) AS negative_time_records
FROM learning_talent
WHERE Time_Spent_Hours < 0;

SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN Completion_Date IS NULL AND Status = 'Completed' THEN 1 ELSE 0 END) AS missing_completion_dates,
    SUM(CASE WHEN Assessment_Score > 100 THEN 1 ELSE 0 END) AS invalid_scores,
    SUM(CASE WHEN Feedback_Rating > 5 OR Feedback_Rating < 1 THEN 1 ELSE 0 END) AS invalid_ratings,
    SUM(CASE WHEN Time_Spent_Hours < 0 THEN 1 ELSE 0 END) AS negative_time_records
FROM learning_talent;

SELECT
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completed_enrollments,
    SUM(Is_Overdue) AS overdue_enrollments,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_assessment_score,
    ROUND(AVG(Feedback_Rating), 2) AS avg_feedback_rating,
    ROUND(AVG(Time_Spent_Hours), 2) AS avg_learning_hours
FROM learning_talent;

SELECT
    COUNT(DISTINCT Employee_ID) AS unique_employees,
    COUNT(DISTINCT Course_ID) AS unique_courses,
    COUNT(DISTINCT Department) AS departments,
    COUNT(DISTINCT Region) AS regions
FROM learning_talent;

SELECT
    Department,
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 2) AS avg_rating
FROM learning_talent
GROUP BY Department
ORDER BY completion_rate_pct DESC;

SELECT
    Department,
    Status,
    COUNT(*) AS record_count
FROM learning_talent
GROUP BY Department, Status
ORDER BY Department, record_count DESC;


SELECT
    Region,
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct
FROM learning_talent
GROUP BY Region
ORDER BY completion_rate_pct DESC;


SELECT
    Mandatory,
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    SUM(Is_Overdue) AS overdue_count
FROM learning_talent
GROUP BY Mandatory;

SELECT
    Course_ID,
    Course_Name,
    Course_Category,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 2) AS avg_rating
FROM learning_talent
GROUP BY Course_ID, Course_Name, Course_Category
ORDER BY completion_rate_pct DESC;

SELECT
    Course_ID,
    Course_Name,
    Course_Category,
    COUNT(*) AS enrollments,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct
FROM learning_talent
GROUP BY Course_ID, Course_Name, Course_Category
HAVING completion_rate_pct < 60
ORDER BY completion_rate_pct ASC;

SELECT
    Course_Category,
    COUNT(*) AS total_enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score,
    ROUND(AVG(Feedback_Rating), 2) AS avg_rating
FROM learning_talent
GROUP BY Course_Category
ORDER BY completion_rate_pct DESC;

SELECT
    Course_Category,
    ROUND(AVG(CASE WHEN Is_Completed = 1 THEN Days_to_Complete END), 2) AS avg_days_to_complete
FROM learning_talent
GROUP BY Course_Category
ORDER BY avg_days_to_complete;


SELECT
    Enrollment_Month,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(AVG(Assessment_Score), 2) AS avg_score
FROM learning_talent
GROUP BY Enrollment_Month
ORDER BY Enrollment_Month;

SELECT
    Enrollment_Year,
    Enrollment_Quarter,
    COUNT(*) AS enrollments,
    SUM(Is_Completed) AS completions,
    ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct
FROM learning_talent
GROUP BY Enrollment_Year, Enrollment_Quarter
ORDER BY Enrollment_Year, Enrollment_Quarter;


SELECT
    Status,
    COUNT(*) AS total_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM learning_talent), 2) AS percentage_of_total
FROM learning_talent
GROUP BY Status
ORDER BY total_records DESC;

SELECT
    Completion_Bucket,
    COUNT(*) AS total_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM learning_talent), 2) AS percentage
FROM learning_talent
GROUP BY Completion_Bucket
ORDER BY total_records DESC;

WITH course_performance AS (
    SELECT
        Course_ID,
        Course_Name,
        COUNT(*) AS enrollments,
        ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct
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
ORDER BY completion_rank;

WITH department_performance AS (
    SELECT
        Department,
        COUNT(*) AS enrollments,
        ROUND(SUM(Is_Completed) * 100.0 / COUNT(*), 2) AS completion_rate_pct
    FROM learning_talent
    GROUP BY Department
)
SELECT
    Department,
    enrollments,
    completion_rate_pct,
    DENSE_RANK() OVER (ORDER BY completion_rate_pct DESC) AS department_rank
FROM department_performance
ORDER BY department_rank;


SELECT
    Department,
    COUNT(*) AS overdue_mandatory_enrollments
FROM learning_talent
WHERE Mandatory = 'Yes' AND Is_Overdue = 1
GROUP BY Department
ORDER BY overdue_mandatory_enrollments DESC;

SELECT
    SUM(CASE WHEN Assessment_Score IS NULL THEN 1 ELSE 0 END) AS missing_scores,
    SUM(CASE WHEN Feedback_Rating IS NULL THEN 1 ELSE 0 END) AS missing_ratings,
    SUM(CASE WHEN Completion_Date IS NULL THEN 1 ELSE 0 END) AS missing_completion_dates,
    SUM(CASE WHEN Days_to_Complete IS NULL THEN 1 ELSE 0 END) AS missing_days_to_complete
FROM learning_talent;
