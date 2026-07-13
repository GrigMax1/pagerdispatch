-- Dispatches table: Stores all dispatch records
CREATE TABLE IF NOT EXISTS dispatches (
    dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispatch_number TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    situation TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active',
    swat_required BOOLEAN DEFAULT 0,
    detectives_required BOOLEAN DEFAULT 0,
    traffic_required BOOLEAN DEFAULT 0,
    message_id INTEGER UNIQUE,
    closed_at DATETIME,
    closed_by TEXT
);

-- Dispatch logs table: Tracks all actions on dispatches
CREATE TABLE IF NOT EXISTS dispatch_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispatch_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    user_name TEXT NOT NULL,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (dispatch_id) REFERENCES dispatches(dispatch_id)
);

-- Officer status tracking table: Tracks officer responses
CREATE TABLE IF NOT EXISTS officer_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispatch_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dispatch_id) REFERENCES dispatches(dispatch_id),
    UNIQUE(dispatch_id, user_id)
);

-- Bot settings table: Stores bot configuration and state
CREATE TABLE IF NOT EXISTS bot_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better query performance
CREATE INDEX IF NOT EXISTS idx_dispatches_status ON dispatches(status);
CREATE INDEX IF NOT EXISTS idx_dispatches_created_at ON dispatches(created_at);
CREATE INDEX IF NOT EXISTS idx_dispatch_logs_dispatch_id ON dispatch_logs(dispatch_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_logs_timestamp ON dispatch_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_officer_responses_dispatch_id ON officer_responses(dispatch_id);
CREATE INDEX IF NOT EXISTS idx_officer_responses_user_id ON officer_responses(user_id);