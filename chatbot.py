"""
chatbot.py

The chatbot answers questions using already uploaded candidate data.
It uses simple Python answers first, then OpenAI if the question is more open.
"""

import os

from openai import OpenAI


def format_candidate_line(candidate):
    """Create one short text line for chatbot answers."""
    return (
        f"{candidate['name']} - {candidate['match_score']}% "
        f"({candidate['category']}), skills: {', '.join(candidate['skills'])}"
    )


def answer_with_rules(question, candidates):
    """Answer common recruiter questions without calling OpenAI."""
    lower_question = question.lower()

    if not candidates:
        return "No resumes have been uploaded yet."

    sorted_candidates = sorted(candidates, key=lambda c: c["match_score"], reverse=True)

    if "top" in lower_question:
        top_candidates = sorted_candidates[:10]
        return "\n".join(format_candidate_line(candidate) for candidate in top_candidates)

    if "most experience" in lower_question:
        best = max(candidates, key=lambda c: c["years_experience"])
        return f"{best['name']} has the most experience with {best['years_experience']} years listed."

    if "compare" in lower_question:
        mentioned_candidates = [
            candidate for candidate in candidates
            if candidate["name"].lower() in lower_question
        ]
        if len(mentioned_candidates) >= 2:
            lines = [format_candidate_line(candidate) for candidate in mentioned_candidates[:2]]
            return "\n".join(lines)

    if "missing" in lower_question and "skill" in lower_question:
        lines = []
        for candidate in sorted_candidates[:5]:
            missing = ", ".join(candidate["missing_skills"]) or "None"
            lines.append(f"{candidate['name']}: {missing}")
        return "\n".join(lines)

    for candidate in candidates:
        for skill in candidate["skills"]:
            if skill.lower() in lower_question:
                matches = [
                    item for item in candidates
                    if skill.lower() in " ".join(item["skills"]).lower()
                ]
                return "\n".join(format_candidate_line(item) for item in matches)

    if "why" in lower_question or "selected" in lower_question:
        for candidate in candidates:
            if candidate["name"].lower() in lower_question:
                return candidate["recommendation"]

    return ""


def build_candidate_context(candidates):
    """Turn candidate dictionaries into text for the AI model."""
    lines = []
    for candidate in candidates:
        lines.append(
            f"Name: {candidate['name']}\n"
            f"Score: {candidate['match_score']}\n"
            f"Category: {candidate['category']}\n"
            f"Skills: {', '.join(candidate['skills'])}\n"
            f"Experience Years: {candidate['years_experience']}\n"
            f"Recommendation: {candidate['recommendation']}\n"
        )
    return "\n---\n".join(lines)


def answer_with_ai(question, candidates):
    """Use OpenAI for flexible questions when an API key is configured."""
    if not os.getenv("OPENAI_API_KEY"):
        return "I can answer top candidates, skills, experience, and missing skills. Add OPENAI_API_KEY for deeper AI chat."

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an HR assistant. Answer only from the candidate data provided.",
                },
                {"role": "user", "content": build_candidate_context(candidates)},
                {"role": "user", "content": question},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception:
        return "The AI assistant could not answer right now. Please check your OpenAI API key."


def answer_question(question, candidates):
    """Main chatbot function used by the Streamlit app."""
    rule_answer = answer_with_rules(question, candidates)
    if rule_answer:
        return rule_answer
    return answer_with_ai(question, candidates)
