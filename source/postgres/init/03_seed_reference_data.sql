-- ============================================================
-- SMART OFFICE
-- Reference Data
-- ============================================================


-- ============================================================
-- OFFICES
-- ============================================================

INSERT INTO office.offices (
    office_code,
    office_name,
    city,
    address,
    timezone,
    capacity,
    status
)
VALUES
(
    'HN01',
    'Hanoi Head Office',
    'Hanoi',
    'Lang Ha, Dong Da, Hanoi',
    'Asia/Ho_Chi_Minh',
    300,
    'ACTIVE'
),
(
    'HCM01',
    'Ho Chi Minh Office',
    'Ho Chi Minh City',
    'District 1, Ho Chi Minh City',
    'Asia/Ho_Chi_Minh',
    150,
    'ACTIVE'
),
(
    'DN01',
    'Da Nang Office',
    'Da Nang',
    'Hai Chau, Da Nang',
    'Asia/Ho_Chi_Minh',
    100,
    'ACTIVE'
)
ON CONFLICT (office_code) DO NOTHING;


INSERT INTO hr.departments (
    department_code,
    department_name,
    status
)
VALUES
    ('EXEC', 'Executive', 'ACTIVE'),
    ('HR', 'Human Resources', 'ACTIVE'),
    ('FIN', 'Finance', 'ACTIVE'),
    ('DATA', 'Data & Analytics', 'ACTIVE'),
    ('ENG', 'Engineering', 'ACTIVE'),
    ('PRODUCT', 'Product', 'ACTIVE'),
    ('MKT', 'Marketing', 'ACTIVE'),
    ('OPS', 'Operations', 'ACTIVE'),
    ('LEGAL', 'Legal & Compliance', 'ACTIVE'),
    ('IT', 'Information Technology', 'ACTIVE')
ON CONFLICT (department_code) DO NOTHING;

INSERT INTO hr.positions (
    position_code,
    title,
    level,
    status
)
VALUES

    ('CEO', 'Chief Executive Officer', 'EXECUTIVE', 'ACTIVE'),
    ('CFO', 'Chief Financial Officer', 'EXECUTIVE', 'ACTIVE'),
    ('CTO', 'Chief Technology Officer', 'EXECUTIVE', 'ACTIVE'),

    ('HR_MANAGER', 'HR Manager', 'MANAGER', 'ACTIVE'),
    ('HR_SPECIALIST', 'HR Specialist', 'STAFF', 'ACTIVE'),

    ('FIN_MANAGER', 'Finance Manager', 'MANAGER', 'ACTIVE'),
    ('ACCOUNTANT', 'Accountant', 'STAFF', 'ACTIVE'),
    ('FIN_ANALYST', 'Financial Analyst', 'STAFF', 'ACTIVE'),

    ('DATA_MANAGER', 'Data Manager', 'MANAGER', 'ACTIVE'),
    ('DATA_ENGINEER', 'Data Engineer', 'STAFF', 'ACTIVE'),
    ('DATA_ANALYST', 'Data Analyst', 'STAFF', 'ACTIVE'),
    ('DATA_SCIENTIST', 'Data Scientist', 'STAFF', 'ACTIVE'),

    ('ENG_MANAGER', 'Engineering Manager', 'MANAGER', 'ACTIVE'),
    ('BACKEND_ENGINEER', 'Backend Engineer', 'STAFF', 'ACTIVE'),
    ('FRONTEND_ENGINEER', 'Frontend Engineer', 'STAFF', 'ACTIVE'),
    ('MOBILE_ENGINEER', 'Mobile Engineer', 'STAFF', 'ACTIVE'),
    ('QA_ENGINEER', 'QA Engineer', 'STAFF', 'ACTIVE'),

    ('PRODUCT_MANAGER', 'Product Manager', 'MANAGER', 'ACTIVE'),
    ('BUSINESS_ANALYST', 'Business Analyst', 'STAFF', 'ACTIVE'),
    ('PRODUCT_OWNER', 'Product Owner', 'STAFF', 'ACTIVE'),

    ('MKT_MANAGER', 'Marketing Manager', 'MANAGER', 'ACTIVE'),
    ('PERFORMANCE_MARKETER', 'Performance Marketer', 'STAFF', 'ACTIVE'),
    ('CONTENT_SPECIALIST', 'Content Specialist', 'STAFF', 'ACTIVE'),

    ('OPS_MANAGER', 'Operations Manager', 'MANAGER', 'ACTIVE'),
    ('OPS_SPECIALIST', 'Operations Specialist', 'STAFF', 'ACTIVE'),

    ('LEGAL_MANAGER', 'Legal Manager', 'MANAGER', 'ACTIVE'),
    ('LEGAL_SPECIALIST', 'Legal Specialist', 'STAFF', 'ACTIVE'),

    ('IT_MANAGER', 'IT Manager', 'MANAGER', 'ACTIVE'),
    ('SYSTEM_ADMIN', 'System Administrator', 'STAFF', 'ACTIVE'),
    ('IT_SUPPORT', 'IT Support Specialist', 'STAFF', 'ACTIVE')

ON CONFLICT (position_code) DO NOTHING;
