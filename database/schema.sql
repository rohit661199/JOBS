-- Database schema for Autonomous Job Search & Application Agent

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text_hash TEXT UNIQUE NOT NULL,
    profile_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    source_url TEXT UNIQUE NOT NULL,
    source_platform TEXT NOT NULL,
    raw_description TEXT NOT NULL,
    salary_range TEXT,
    employment_type TEXT,
    posted_date TEXT,
    fingerprint TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL UNIQUE,
    overall_match_score REAL NOT NULL,
    skills_score REAL NOT NULL,
    tech_stack_score REAL NOT NULL,
    experience_score REAL NOT NULL,
    domain_score REAL NOT NULL,
    ats_keyword_score REAL NOT NULL,
    strengths TEXT NOT NULL, -- JSON array
    weaknesses TEXT NOT NULL, -- JSON array
    reasoning TEXT NOT NULL,
    decision TEXT NOT NULL, -- APPLY, MAYBE, REJECT
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL, -- QUEUED, APPLIED, HITL_PAUSED, INTERVIEW, ASSESSMENT, REJECTED, OFFER
    applied_at TIMESTAMP,
    resume_file_used TEXT NOT NULL,
    cover_letter_text TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_fingerprint ON jobs(fingerprint);
CREATE INDEX IF NOT EXISTS idx_evaluations_decision ON job_evaluations(decision);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
