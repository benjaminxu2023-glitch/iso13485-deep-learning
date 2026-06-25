CREATE TABLE IF NOT EXISTS student_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    province TEXT NOT NULL CHECK(province IN ('zhejiang', 'jiangsu', 'shanghai')),
    score INTEGER NOT NULL CHECK(score >= 0 AND score <= 750),
    rank INTEGER NOT NULL CHECK(rank > 0),
    subject_category TEXT,
    subjects TEXT NOT NULL,
    preferred_cities TEXT,
    preferred_majors TEXT,
    rejected_majors TEXT,
    budget_limit INTEGER,
    accept_adjustment INTEGER DEFAULT 1,
    accept_sino_foreign INTEGER DEFAULT 0,
    risk_preference TEXT DEFAULT 'balanced',
    health_limits TEXT,
    career_direction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,
    year INTEGER NOT NULL,
    university_name TEXT NOT NULL,
    university_code TEXT,
    major_name TEXT NOT NULL,
    major_code TEXT,
    major_group_code TEXT,
    batch TEXT NOT NULL DEFAULT '普通类',
    plan_type TEXT NOT NULL DEFAULT 'major',
    enrollment_count INTEGER,
    min_score INTEGER,
    min_rank INTEGER,
    avg_score INTEGER,
    avg_rank INTEGER,
    subject_requirements TEXT,
    subject_category TEXT,
    city TEXT,
    campus TEXT,
    tuition INTEGER,
    remarks TEXT,
    UNIQUE(province, year, university_code, major_code, batch)
);

CREATE TABLE IF NOT EXISTS admission_plan_current_year (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,
    year INTEGER NOT NULL DEFAULT 2025,
    university_name TEXT NOT NULL,
    university_code TEXT,
    major_name TEXT NOT NULL,
    major_code TEXT,
    major_group_code TEXT,
    batch TEXT NOT NULL DEFAULT '普通类',
    plan_type TEXT NOT NULL DEFAULT 'major',
    enrollment_count INTEGER,
    subject_requirements TEXT,
    subject_category TEXT,
    tuition INTEGER,
    city TEXT,
    campus TEXT,
    charter_special_conditions TEXT,
    remarks TEXT,
    UNIQUE(province, university_code, major_code, batch)
);

CREATE TABLE IF NOT EXISTS charter_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_code TEXT NOT NULL,
    university_name TEXT NOT NULL,
    province TEXT NOT NULL,
    risk_items TEXT NOT NULL,
    audit_source TEXT,
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_code, province)
);

CREATE TABLE IF NOT EXISTS recommendation_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, stage, input_hash)
);

CREATE INDEX IF NOT EXISTS idx_history_province_year ON admission_history(province, year);
CREATE INDEX IF NOT EXISTS idx_history_university ON admission_history(university_code);
CREATE INDEX IF NOT EXISTS idx_plan_province ON admission_plan_current_year(province);
CREATE INDEX IF NOT EXISTS idx_cache_session ON recommendation_cache(session_id, stage);
