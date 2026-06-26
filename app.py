"""
TalentLens AI Streamlit App

Run with:
streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from chatbot import answer_question
from database import (
    create_tables,
    delete_all_candidates,
    ensure_upload_folder,
    get_all_candidates,
    get_dashboard_counts,
    save_candidate,
)
from matching import clean_keywords, match_candidate
from resume_parser import extract_resume_text, parse_resume
from utils import (
    candidates_to_dataframe,
    check_login,
    get_shortlisted_candidates,
    sort_candidates,
)


st.set_page_config(page_title="TalentLens AI", page_icon="🔎", layout="wide")


def apply_simple_theme():
    """Add a polished blue and white theme to the Streamlit page."""
    css_file = Path("static/styles.css")
    css_text = css_file.read_text()
    st.markdown(
        f"<style>{css_text}</style>",
        unsafe_allow_html=True,
    )


def show_login_page():
    """Display a clean login screen."""
    left_column, right_column = st.columns([1.2, 1])

    with left_column:
        st.markdown(
            """
            <div class="hero-box">
                <p class="hero-title">TalentLens AI</p>
                <p class="hero-subtitle">Review resumes, score matches, and shortlist candidates faster.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("Default HR login: username `hr`, password `talentlens123`")

    with right_column:
        st.subheader("HR Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

        if login_button:
            if check_login(username, password):
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid login. Try username: hr and password: talentlens123")


def show_home_header():
    """Show the main app header after login."""
    st.markdown(
        """
        <div class="hero-box">
            <p class="hero-title">TalentLens AI</p>
            <p class="hero-subtitle">Upload resumes, match them to a role, and review the strongest candidates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_uploaded_file(uploaded_file):
    """Save an uploaded file into the uploads folder and return its path."""
    file_path = Path("uploads") / uploaded_file.name
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return str(file_path)


def read_job_description(uploaded_job_file, pasted_job_description):
    """Return job description text from either a file upload or text area."""
    if pasted_job_description.strip():
        return pasted_job_description.strip()

    if uploaded_job_file:
        file_path = save_uploaded_file(uploaded_job_file)
        try:
            return extract_resume_text(file_path)
        except ValueError as error:
            st.error(str(error))
            return ""

    return ""


def show_dashboard():
    """Show simple dashboard metrics."""
    counts = get_dashboard_counts()
    st.subheader("Dashboard")
    col1, col2, col3 = st.columns(3, gap="medium")
    col1.metric("Resumes Uploaded", counts["uploaded"])
    col2.metric("Shortlisted", counts["shortlisted"])
    col3.metric("Rejected", counts["rejected"])


def show_upload_section():
    """Allow HR to upload resumes and enter matching requirements."""
    st.subheader("Analyze Resumes")

    resume_column, role_column = st.columns([1, 1], gap="large")

    with resume_column:
        with st.container(border=True):
            st.markdown("**Upload resumes**")
            uploaded_resumes = st.file_uploader(
                "PDF or DOCX resumes",
                type=["pdf", "docx"],
                accept_multiple_files=True,
            )

    with role_column:
        with st.container(border=True):
            st.markdown("**Job description**")
            pasted_job_description = st.text_area("Paste job description", height=130)
            uploaded_job_file = st.file_uploader("Or upload job description file", type=["pdf", "docx"])

    with st.container(border=True):
        st.markdown("**Keywords**")
        keyword_text = st.text_area(
            "Important skills or keywords",
            value="Python\nFastAPI\nDocker\nSQL\nGit\nMachine Learning",
            height=110,
        )

    if st.button("Analyze Resumes"):
        if not uploaded_resumes:
            st.warning("Please upload at least one resume.")
            return

        job_description = read_job_description(uploaded_job_file, pasted_job_description)
        if not job_description:
            st.warning("Please paste or upload a job description.")
            return

        keywords = clean_keywords(keyword_text)
        if not keywords:
            st.warning("Please enter at least one keyword.")
            return

        with st.spinner("Reading resumes and calculating matches..."):
            for uploaded_resume in uploaded_resumes:
                try:
                    file_path = save_uploaded_file(uploaded_resume)
                    candidate = parse_resume(file_path)
                    candidate["file_name"] = uploaded_resume.name
                    matched_candidate = match_candidate(candidate, job_description, keywords)
                    save_candidate(matched_candidate)
                    st.success(f"Analyzed {uploaded_resume.name}")
                except ValueError as error:
                    st.error(f"{uploaded_resume.name}: {error}")


def show_candidates_table(candidates):
    """Display candidates in a sortable table."""
    st.subheader("Candidate Ranking")

    if not candidates:
        st.info("No resumes uploaded yet.")
        return

    sort_option = st.selectbox(
        "Sort candidates by",
        ["Highest Score", "Experience", "Education", "Skills", "Name"],
    )
    sorted_candidates = sort_candidates(candidates, sort_option)
    dataframe = candidates_to_dataframe(sorted_candidates)
    st.dataframe(dataframe, use_container_width=True)


def show_candidate_categories(candidates):
    """Separate candidates into the four required match categories."""
    st.subheader("Candidate Categories")

    if not candidates:
        st.info("Upload resumes to see categories.")
        return

    categories = ["Excellent Match", "Good Match", "Average Match", "Not Suitable"]
    tabs = st.tabs(categories)

    for index, category in enumerate(categories):
        category_candidates = [
            candidate for candidate in candidates
            if candidate["category"] == category
        ]
        with tabs[index]:
            if category_candidates:
                st.dataframe(
                    candidates_to_dataframe(category_candidates),
                    use_container_width=True,
                )
            else:
                st.info(f"No candidates in {category}.")


def show_candidate_details(candidates):
    """Let HR choose one candidate and inspect details."""
    st.subheader("Candidate Details")

    if not candidates:
        st.info("Upload resumes to view candidate details.")
        return

    candidate_names = [candidate["name"] for candidate in candidates]
    selected_name = st.selectbox("Select candidate", candidate_names)
    selected_candidate = next(candidate for candidate in candidates if candidate["name"] == selected_name)

    st.markdown(f"### {selected_candidate['name']}")
    st.markdown(
        f"<span class='score-pill'>{selected_candidate['match_score']}% match</span>",
        unsafe_allow_html=True,
    )
    st.progress(int(selected_candidate["match_score"]))
    st.write(f"**Category:** {selected_candidate['category']}")
    st.write(f"**Recommendation:** {selected_candidate['recommendation']}")
    st.write("**Resume Summary**")
    st.write(selected_candidate["resume_summary"] or "No summary available.")
    st.write("**Skills**")
    st.write(", ".join(selected_candidate["skills"]) or "No skills found.")
    st.write("**Experience**")
    st.write(selected_candidate["experience"] or "No experience section found.")
    st.write("**Education**")
    st.write(selected_candidate["education"] or "No education section found.")
    st.write("**Projects**")
    st.write(selected_candidate["projects"] or "No projects section found.")


def show_chatbot(candidates):
    """Display a simple AI chatbot for recruiter questions."""
    st.subheader("AI Chat Assistant")

    question = st.text_input("Ask about uploaded candidates")
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
            return
        answer = answer_question(question, candidates)
        st.markdown(answer.replace("\n", "  \n"))


def show_export(candidates):
    """Allow HR to export shortlisted candidates to CSV."""
    st.subheader("Export Shortlist")

    shortlisted = get_shortlisted_candidates(candidates)
    if not shortlisted:
        st.info("No shortlisted candidates yet.")
        return

    csv_data = candidates_to_dataframe(shortlisted).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download shortlisted candidates as CSV",
        data=csv_data,
        file_name="shortlisted_candidates.csv",
        mime="text/csv",
    )


def main():
    """Start the TalentLens AI Streamlit app."""
    apply_simple_theme()
    create_tables()
    ensure_upload_folder()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        show_login_page()
        return

    st.sidebar.title("TalentLens AI")
    st.sidebar.write("Logged in as HR")
    if st.sidebar.button("Clear All Candidates"):
        delete_all_candidates()
        st.rerun()
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    show_home_header()

    show_dashboard()
    show_upload_section()

    candidates = get_all_candidates()
    show_candidates_table(candidates)
    show_candidate_categories(candidates)
    show_candidate_details(candidates)
    show_chatbot(candidates)
    show_export(candidates)


if __name__ == "__main__":
    main()
