-- Fix section strings that are literal 'None' in student_page1
UPDATE student_page1 SET section = NULL WHERE section = 'None';

-- Insert missing classes from student_page1 into admin_student_classes
INSERT IGNORE INTO admin_student_classes (admin_id, class, section, created_at)
SELECT 1, LEFT(sp.class, 50), sp.section, CURRENT_TIMESTAMP
FROM (
    SELECT DISTINCT class, section
    FROM student_page1
    WHERE class IS NOT NULL AND class != ''
) AS sp
WHERE NOT EXISTS (
    SELECT 1 
    FROM admin_student_classes asc2 
    WHERE asc2.class = LEFT(sp.class, 50)
    AND (
        (asc2.section = sp.section) OR 
        (asc2.section IS NULL AND sp.section IS NULL)
    )
);
