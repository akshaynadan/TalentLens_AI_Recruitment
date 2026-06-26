"""
utils.py

Small helper functions shared by the Streamlit app.
"""

import pandas as pd


DEFAULT_USERNAME = "hr"
DEFAULT_PASSWORD = "talentlens123"


def check_login(username, password):
    """Check the simple default HR login."""
    return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD


def candidates_to_dataframe(candidates):
    """Convert candidate dictionaries into a clean table for Streamlit."""
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "Name": candidate["name"],
                "Email": candidate["email"],
                "Phone": candidate["phone"],
                "Skills": ", ".join(candidate["skills"]),
                "Years Experience": candidate["years_experience"],
                "Score": candidate["match_score"],
                "Category": candidate["category"],
                "Matched Skills": ", ".join(candidate["matched_skills"]),
                "Missing Skills": ", ".join(candidate["missing_skills"]),
            }
        )
    return pd.DataFrame(rows)


def sort_candidates(candidates, sort_option):
    """Sort candidates based on the dropdown selected by HR."""
    if sort_option == "Highest Score":
        return sorted(candidates, key=lambda c: c["match_score"], reverse=True)
    if sort_option == "Experience":
        return sorted(candidates, key=lambda c: c["years_experience"], reverse=True)
    if sort_option == "Education":
        return sorted(candidates, key=lambda c: c["education"], reverse=True)
    if sort_option == "Skills":
        return sorted(candidates, key=lambda c: len(c["skills"]), reverse=True)
    if sort_option == "Name":
        return sorted(candidates, key=lambda c: c["name"])
    return candidates


def get_shortlisted_candidates(candidates):
    """Return candidates that HR will likely want to export."""
    return [
        candidate for candidate in candidates
        if candidate["category"] in ["Excellent Match", "Good Match"]
    ]
