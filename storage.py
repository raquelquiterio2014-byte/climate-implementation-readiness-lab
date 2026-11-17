"""Local review history; not immutable or suitable for sensitive data."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from core import fingerprint

DECISIONS = ('needs_revision', 'reviewed', 'rejected')

def init_db(db):
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp_utc TEXT NOT NULL,
            project_id TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL,
            rationale TEXT NOT NULL, assessment_sha256 TEXT NOT NULL, ai_sha256 TEXT NOT NULL)''')

def save_review(db, project_id, reviewer, decision, rationale, assessment, ai_output):
    if decision not in DECISIONS:
        raise ValueError('Invalid review decision')
    if len(reviewer.strip()) < 2 or len(rationale.strip()) < 5:
        raise ValueError('Reviewer and substantive rationale required')
    if assessment.get('project_id') != project_id:
        raise ValueError('Project mismatch: review cannot be saved')
    init_db(db)
    with sqlite3.connect(db) as con:
        con.execute('''INSERT INTO reviews (timestamp_utc,project_id,reviewer,decision,rationale,assessment_sha256,ai_sha256)
                       VALUES (?,?,?,?,?,?,?)''',
                    (datetime.now(timezone.utc).isoformat(), project_id, reviewer.strip(), decision,
                     rationale.strip(), fingerprint(assessment), fingerprint(ai_output)))

def list_reviews(db):
    init_db(db)
    with sqlite3.connect(db) as con:
        con.row_factory = sqlite3.Row
        return [dict(row) for row in con.execute('SELECT * FROM reviews ORDER BY id DESC')]
