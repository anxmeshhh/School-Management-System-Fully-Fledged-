-- 1. Fix the column size on your VPS so it can hold the full 'TODDLER MELLON' string
ALTER TABLE admin_student_classes MODIFY class VARCHAR(50) NULL;

-- Fix the section column to ensure it allows NULL values
ALTER TABLE admin_student_classes MODIFY section VARCHAR(10) NULL;

-- 2. Delete the incorrectly truncated short classes that were inserted
DELETE FROM admin_student_classes WHERE class IN ('TODDLER ME', 'JUNIOR MEL', 'MASTER MEL', 'RAISING ME', 'GRAND MELL');

-- 3. Re-insert them with their full names from student_page1
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
