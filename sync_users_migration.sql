-- Migration Script: Sync Admins and Teachers into admin_manage_users

-- 1. Sync Admins (assigns role 'admin', skips if email already exists)
INSERT INTO admin_manage_users (name, email, username, password, role, created_at)
SELECT a.full_name, a.email, a.email, a.password, 'admin', a.created_at
FROM admins a
WHERE NOT EXISTS (
    SELECT 1 FROM admin_manage_users amu WHERE amu.email = a.email
);

-- 2. Sync Teachers (assigns role 'teacher', skips if email already exists)
INSERT INTO admin_manage_users (name, email, username, password, role, created_at)
SELECT t.name, t.email, t.email, t.password, 'teacher', t.created_at
FROM teachers t
WHERE NOT EXISTS (
    SELECT 1 FROM admin_manage_users amu WHERE amu.email = t.email
);
