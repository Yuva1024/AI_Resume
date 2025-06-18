import streamlit as st
import openai
import pdfkit
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Resume Agent", layout="centered")

st.title("📄 AI Resume Generator")
st.markdown("Generate an ATS-optimized resume tailored to your job role using AI.")

# --- Input Section ---
user_type = st.selectbox("User Type", ["Fresher", "Early Career", "Freelancer", "Job Switcher"])
job_role = st.text_input("Target Job Role", placeholder="e.g., Data Analyst")
tone = st.radio("Tone", ["Formal", "Confident", "Creative"], horizontal=True)
layout = st.selectbox("Resume Layout Style", ["Minimal", "Modern", "Creative"])
resume_file = st.file_uploader("Upload Existing Resume (PDF or DOCX)", type=["pdf", "docx"])

st.subheader("Fill in or update these fields:")

education = st.text_area("Education Details", height=100)
experience = st.text_area("Work Experience", height=150)
projects = st.text_area("Projects", height=100)
skills = st.text_area("Skills (comma-separated)")
certifications = st.text_area("Certifications")
portfolio = st.text_input("LinkedIn or Portfolio URL")

# --- AI Prompt Template ---
def build_prompt():
    return f"""
You are an expert resume writer trained in ATS-optimized formatting, persuasive writing, and professional branding.

Rewrite the following resume into a clean, concise, and tailored resume for the job role: **{job_role}**.
Use a **{tone}** tone and a **{layout}** layout.

---

User Type: {user_type}

Education:
{education}

Experience:
{experience}

Projects:
{projects}

Skills:
{skills}

Certifications:
{certifications}

Portfolio / LinkedIn:
{portfolio}

Instructions:
- Add a professional summary at the top.
- Use action verbs and measurable outcomes.
- Group skills logically.
- Format into sections: Summary, Experience, Education, Skills, Projects, Certifications.
"""

# --- Session State for Resume Output ---
if "resume_output" not in st.session_state:
    st.session_state.resume_output = ""

# --- Process AI + Output ---
if st.button("Generate Resume"):
    with st.spinner("Generating resume with AI..."):
        try:
            if not openai.api_key:
                st.error("❌ OpenAI API key not found. Please check your .env file.")
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": build_prompt()
                    }],
                    temperature=0.7
                )
                resume_output = response.choices[0].message["content"]
                st.session_state.resume_output = resume_output
                st.success("✅ Resume generated!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Display and Download Section ---
if st.session_state.resume_output:
    st.subheader("📄 AI-Generated Resume")
    st.text_area("Output", st.session_state.resume_output, height=400, disabled=True)
    st.download_button("⬇ Download as .txt", st.session_state.resume_output, file_name="resume.txt")

    # Optional PDF conversion
    if st.button("⬇ Download as PDF"):
        try:
            html_resume = f"<pre>{st.session_state.resume_output}</pre>"
            pdfkit.from_string(html_resume, "resume.pdf")
            with open("resume.pdf", "rb") as f:
                st.download_button("📎 Download PDF", f, file_name="resume.pdf")
        except Exception as e:
            st.error(f"❌ PDF generation error: {e}")
