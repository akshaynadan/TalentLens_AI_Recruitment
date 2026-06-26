"""
database.py

Small SQLite helper functions for TalentLens AI.
The project keeps database code simple so beginners can follow it easily.
"""

import json
import sqlite3
from pathlib import Path


DATABASE_FILE = "talentlens.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_FILE)


def create_tables():
    """Create the candidates table if it does not already exist."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            certifications TEXT,
            projects TEXT,
            years_experience REAL,
            match_score REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            education_match TEXT,
            projects_match TEXT,
            category TEXT,
            recommendation TEXT,
            resume_summary TEXT,
            file_name TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_candidate(candidate):
    """Save one analyzed candidate dictionary into the database."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO candidates (
            name, email, phone, skills, education, experience, certifications,
            projects, years_experience, match_score, matched_skills,
            missing_skills, education_match, projects_match, category,
            recommendation, resume_summary, file_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate.get("name", "Unknown"),
            candidate.get("email", ""),
            candidate.get("phone", ""),
            json.dumps(candidate.get("skills", [])),
            candidate.get("education", ""),
            candidate.get("experience", ""),
            candidate.get("certifications", ""),
            candidate.get("projects", ""),
            candidate.get("years_experience", 0),
            candidate.get("match_score", 0),
            json.dumps(candidate.get("matched_skills", [])),
            json.dumps(candidate.get("missing_skills", [])),
            candidate.get("education_match", ""),
            candidate.get("projects_match", ""),
            candidate.get("category", "Not Suitable"),
            candidate.get("recommendation", ""),
            candidate.get("resume_summary", ""),
            candidate.get("file_name", ""),
        ),
    )

    connection.commit()
    connection.close()


def get_all_candidates():
    """Return all candidates as a list of dictionaries."""
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM candidates")
    rows = cursor.fetchall()
    connection.close()

    candidates = []
    for row in rows:
        candidate = dict(row)
        candidate["skills"] = json.loads(candidate["skills"] or "[]")
        candidate["matched_skills"] = json.loads(candidate["matched_skills"] or "[]")
        candidate["missing_skills"] = json.loads(candidate["missing_skills"] or "[]")
        candidates.append(candidate)

    return candidates


def delete_all_candidates():
    """Remove all candidates from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM candidates")
    connection.commit()
    connection.close()


def get_dashboard_counts():
    """Calculate simple numbers for the Streamlit dashboard."""
    candidates = get_all_candidates()
    shortlisted = [c for c in candidates if c["category"] in ["Excellent Match", "Good Match"]]
    rejected = [c for c in candidates if c["category"] == "Not Suitable"]

    return {
        "uploaded": len(candidates),
        "shortlisted": len(shortlisted),
        "rejected": len(rejected),
    }


def ensure_upload_folder():
    """Create the uploads folder if it is missing."""
    Path("uploads").mkdir(exist_ok=True)
