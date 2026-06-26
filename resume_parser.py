"""
resume_parser.py

Functions for reading PDF and DOCX resumes and extracting simple profile data.
The AI extraction step is optional. If no OpenAI API key exists, the app still
works using beginner-friendly rule-based extraction.
"""

import os
import re

import docx
import fitz
from openai import OpenAI


COMMON_SKILLS = [
    "Python", "FastAPI", "Streamlit", "Docker", "SQL", "SQLite", "Git",
    "React", "JavaScript", "Machine Learning", "AI", "NLP", "Pandas",
    "NumPy", "Django", "Flask", "AWS", "Azure", "Linux", "REST API",
]


def extract_text_from_pdf(file_path):
    """Read text from a PDF file using PyMuPDF."""
    text = ""
    try:
        document = fitz.open(file_path)
        for page in document:
            text += page.get_text()
        document.close()
    except Exception:
        raise ValueError("Could not read this PDF. It may be invalid or corrupted.")
    return text.strip()


def extract_text_from_docx(file_path):
    """Read text from a DOCX file using python-docx."""
    try:
        document = docx.Document(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
    except Exception:
        raise ValueError("Could not read this DOCX. It may be invalid or corrupted.")
    return "\n".join(paragraphs).strip()


def extract_resume_text(file_path):
    """Choose the correct parser based on the file extension."""
    lower_file_name = file_path.lower()
    if lower_file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    if lower_file_name.endswith(".docx"):
        return extract_text_from_docx(file_path)
    raise ValueError("Only PDF and DOCX files are supported.")


def find_email(text):
    """Find the first email address in the resume text."""
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else ""


def find_phone(text):
    """Find a likely phone number in the resume text."""
    match = re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", text)
    return match.group(0).strip() if match else ""


def guess_name(text):
    """Use the first non-empty line as a simple name guess."""
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line and "@" not in clean_line and len(clean_line.split()) <= 5:
            return clean_line
    return "Unknown Candidate"


def find_skills(text):
    """Search the resume for skills from a small known skills list."""
    found_skills = []
    lower_text = text.lower()

    for skill in COMMON_SKILLS:
        if skill.lower() in lower_text:
            found_skills.append(skill)

    return found_skills


def find_years_experience(text):
    """Look for phrases like '3 years of experience' and return the largest number."""
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", text.lower())
    numbers = [float(match) for match in matches]
    return max(numbers) if numbers else 0


def extract_section(text, section_words):
    """Pull a small text snippet around important section words."""
    lines = text.splitlines()
    selected_lines = []

    for index, line in enumerate(lines):
        lower_line = line.lower()
        if any(word in lower_line for word in section_words):
            selected_lines.extend(lines[index:index + 4])

    return "\n".join(selected_lines).strip()


def summarize_resume(text):
    """Create a short summary from the first few meaningful lines."""
    useful_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " ".join(useful_lines[:5])[:700]


def parse_resume_with_rules(text):
    """Extract resume details using simple Python logic."""
    return {
        "name": guess_name(text),
        "email": find_email(text),
        "phone": find_phone(text),
        "skills": find_skills(text),
        "education": extract_section(text, ["education", "university", "college", "degree"]),
        "experience": extract_section(text, ["experience", "employment", "work history"]),
        "certifications": extract_section(text, ["certification", "certificate"]),
        "projects": extract_section(text, ["project", "portfolio"]),
        "years_experience": find_years_experience(text),
        "resume_summary": summarize_resume(text),
    }


def improve_summary_with_ai(text):
    """Ask OpenAI for a cleaner resume summary when an API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        return ""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Summarize this resume for an HR recruiter in 4 bullet points."},
                {"role": "user", "content": text[:6000]},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception:
        return ""


def parse_resume(file_path):
    """Read a resume file and return extracted candidate information."""
    text = extract_resume_text(file_path)
    if not text:
        raise ValueError("No readable text was found in this resume.")

    candidate = parse_resume_with_rules(text)
    ai_summary = improve_summary_with_ai(text)
    if ai_summary:
        candidate["resume_summary"] = ai_summary
    return candidate
