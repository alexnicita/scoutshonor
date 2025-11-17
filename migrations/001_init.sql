PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS startups (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    stage TEXT NOT NULL,
    domains TEXT DEFAULT '[]',
    location TEXT,
    description TEXT,
    website TEXT,
    mission TEXT,
    stack TEXT DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    startup_id TEXT NOT NULL,
    title TEXT NOT NULL,
    required_skills TEXT DEFAULT '[]',
    nice_to_have_skills TEXT DEFAULT '[]',
    min_years_experience INTEGER DEFAULT 0,
    responsibilities TEXT DEFAULT '[]',
    seniority TEXT NOT NULL,
    location_preference TEXT,
    remote_ok INTEGER DEFAULT 1,
    compensation_range TEXT,
    recruiter_notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (startup_id) REFERENCES startups (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scorecards (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    summary TEXT,
    must_haves TEXT DEFAULT '[]',
    nice_to_haves TEXT DEFAULT '[]',
    evaluation_points TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    current_title TEXT,
    titles TEXT DEFAULT '[]',
    years_experience INTEGER DEFAULT 0,
    skills TEXT DEFAULT '[]',
    domains TEXT DEFAULT '[]',
    locations TEXT DEFAULT '[]',
    timezone TEXT,
    remote_preference INTEGER,
    stage_preferences TEXT DEFAULT '[]',
    linkedin_url TEXT,
    email TEXT,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_candidates_email
    ON candidates (email) WHERE email IS NOT NULL;

CREATE TABLE IF NOT EXISTS profile_sources (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    source TEXT NOT NULL,
    handle TEXT,
    url TEXT,
    notes TEXT,
    imported_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interactions (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    direction TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    status TEXT,
    outcome TEXT,
    metadata TEXT DEFAULT '{}',
    occurred_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sequences (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    name TEXT NOT NULL,
    steps TEXT DEFAULT '[]',
    active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stage_events (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT,
    notes TEXT,
    occurred_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS suppression_list (
    contact TEXT PRIMARY KEY,
    reason TEXT,
    source TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consent_events (
    id TEXT PRIMARY KEY,
    contact TEXT NOT NULL,
    candidate_id TEXT,
    status TEXT NOT NULL,
    source TEXT,
    notes TEXT,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    subject_id TEXT,
    detail TEXT,
    created_at TEXT NOT NULL
);
