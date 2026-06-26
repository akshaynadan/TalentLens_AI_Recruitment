"""
matching.py

Simple resume matching logic. The scoring is intentionally understandable:
skills and keywords matter most, then job description overlap, experience,
education, and projects.
"""

import re


def clean_keywords(keyword_text):
    """Turn comma/newline separated keywords into a clean list."""
    raw_keywords = re.split(r"[,\n]", keyword_text)
    return [keyword.strip() for keyword in raw_keywords if keyword.strip()]


def calculate_text_overlap(resume_text, job_description):
    """Calculate how many job description words appear in the resume."""
    resume_words = set(re.findall(r"\w+", resume_text.lower()))
    job_words = set(re.findall(r"\w+", job_description.lower()))

    useful_job_words = {word for word in job_words if len(word) > 3}
    if not useful_job_words:
        return 0

    matching_words = resume_words.intersection(useful_job_words)
    return len(matching_words) / len(useful_job_words)


def get_candidate_category(score):
    """Convert a numeric score into an HR-friendly category."""
    if score >= 80:
        return "Excellent Match"
    if score >= 60:
        return "Good Match"
    if score >= 40:
        return "Average Match"
    return "Not Suitable"


def education_matches(education_text, job_description):
    """Check whether education looks relevant to the job description."""
    combined_text = f"{education_text} {job_description}".lower()
    degree_words = ["bachelor", "master", "phd", "degree", "computer", "engineering"]
    return "Yes" if any(word in combined_text for word in degree_words) else "Not clear"


def projects_match(projects_text, keywords):
    """Check whether project descriptions mention requested keywords."""
    lower_projects = projects_text.lower()
    for keyword in keywords:
        if keyword.lower() in lower_projects:
            return "Yes"
    return "Not clear"


def build_recommendation(candidate, matched_skills, missing_skills, score):
    """Create a short explanation for why this candidate received the score."""
    if matched_skills:
        skill_text = ", ".join(matched_skills[:5])
    else:
        skill_text = "no major requested skills"

    if missing_skills:
        missing_text = ", ".join(missing_skills[:5])
    else:
        missing_text = "no major missing skills"

    return (
        f"{candidate['name']} scored {score}% because they matched {skill_text}. "
        f"Missing or unclear skills include {missing_text}."
    )


def match_candidate(candidate, job_description, keywords):
    """Add matching scores and recommendation fields to one candidate."""
    candidate_skills = candidate.get("skills", [])
    lower_resume_text = " ".join(
        [
            candidate.get("resume_summary", ""),
            candidate.get("education", ""),
            candidate.get("experience", ""),
            candidate.get("projects", ""),
            " ".join(candidate_skills),
        ]
    ).lower()

    matched_skills = [
        keyword for keyword in keywords if keyword.lower() in lower_resume_text
    ]
    missing_skills = [
        keyword for keyword in keywords if keyword.lower() not in lower_resume_text
    ]

    skill_score = (len(matched_skills) / len(keywords) * 45) if keywords else 0
    description_score = calculate_text_overlap(lower_resume_text, job_description) * 25
    experience_score = min(candidate.get("years_experience", 0), 10) / 10 * 15

    education_match = education_matches(candidate.get("education", ""), job_description)
    education_score = 10 if education_match == "Yes" else 3

    projects_match_value = projects_match(candidate.get("projects", ""), keywords)
    projects_score = 5 if projects_match_value == "Yes" else 1

    total_score = round(skill_score + description_score + experience_score + education_score + projects_score, 1)
    total_score = min(total_score, 100)

    candidate["match_score"] = total_score
    candidate["matched_skills"] = matched_skills
    candidate["missing_skills"] = missing_skills
    candidate["education_match"] = education_match
    candidate["projects_match"] = projects_match_value
    candidate["category"] = get_candidate_category(total_score)
    candidate["recommendation"] = build_recommendation(candidate, matched_skills, missing_skills, total_score)
    return candidate
