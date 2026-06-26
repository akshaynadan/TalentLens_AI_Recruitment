"""
api.py

A tiny FastAPI backend for TalentLens AI.
The Streamlit app is the main user interface, but this file shows how the same
candidate data can be exposed through simple API endpoints.
"""

from fastapi import FastAPI

from database import create_tables, get_all_candidates, get_dashboard_counts


app = FastAPI(title="TalentLens AI API")


@app.on_event("startup")
def startup():
    """Make sure database tables exist when the API starts."""
    create_tables()


@app.get("/")
def home():
    """Return a friendly API welcome message."""
    return {"message": "Welcome to the TalentLens AI API"}


@app.get("/dashboard")
def dashboard():
    """Return dashboard counts for uploaded, shortlisted, and rejected resumes."""
    return get_dashboard_counts()


@app.get("/candidates")
def candidates():
    """Return all analyzed candidates."""
    return get_all_candidates()
