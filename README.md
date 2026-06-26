# TalentLens AI

TalentLens AI is a beginner-friendly AI recruitment assistant built with Python, Streamlit, FastAPI, SQLite, and the OpenAI API.

Recruiters can upload resumes, compare them with a job description, rank candidates, inspect candidate details, chat with an assistant, and export shortlisted applicants.

## Features

- Simple HR login
- Dashboard with uploaded, shortlisted, and rejected counts
- Multiple PDF and DOCX resume uploads
- Job description paste or file upload
- Keyword-based matching
- Resume parsing for name, email, phone, skills, education, experience, certifications, and projects
- Overall match score from 0 to 100
- Matched skills, missing skills, experience, education match, and projects match
- Candidate categories: Excellent Match, Good Match, Average Match, Not Suitable
- Sorting by score, experience, education, skills, or name
- AI chat assistant that answers questions using uploaded candidate data
- Candidate detail view
- CSV export for shortlisted candidates

## Screenshots

screenshots are added in the Output folder after running the project:

- Login page
- Dashboard
- Resume analysis table
- Candidate details
- Chat assistant

## Tech Stack

- Python 3.12
- Streamlit for the frontend
- FastAPI for a small backend API
- SQLite for local storage
- OpenAI API for optional AI summaries and chat
- PyMuPDF for PDF parsing
- python-docx for DOCX parsing

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## OpenAI Setup

The app still works without an OpenAI API key by using simple rule-based extraction and chat answers.

To enable AI summaries and deeper chat:

```bash
export OPENAI_API_KEY="your-api-key"
```

Optional:

```bash
export OPENAI_MODEL="gpt-4o-mini"
```

## How To Run

Start the Streamlit app:

```bash
streamlit run app.py
```

Default login:

- Username: `hr`
- Password: `talentlens123`

Start the optional FastAPI backend:

```bash
uvicorn api:app --reload
```

Then open:

- Streamlit: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

## Folder Structure

```text
talentlens-ai/
├── app.py
├── api.py
├── database.py
├── resume_parser.py
├── matching.py
├── chatbot.py
├── utils.py
├── requirements.txt
├── README.md
├── templates/
├── static/
└── uploads/
```

## How The Matching Works

The matching logic is intentionally simple so beginners can explain it:

1. Check how many requested keywords appear in the resume.
2. Compare resume text with job description words.
3. Add points for years of experience.
4. Check whether education looks relevant.
5. Check whether projects mention requested skills.

The final score is converted into a category:

- 80-100: Excellent Match
- 60-79: Good Match
- 40-59: Average Match
- Below 40: Not Suitable

## Error Handling

The app handles:

- Invalid PDF files
- Corrupted DOCX files
- Empty uploads
- Missing OpenAI API key
- No resumes uploaded
- No job description entered
- Missing keywords

## Future Improvements

- Add real user registration
- Store uploaded files in cloud storage
- Add better resume section detection
- Improve AI extraction with structured JSON output
- Add candidate comparison charts
- Add interview question generation
- Add Docker deployment
- Add automated tests
