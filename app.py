import streamlit as st
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import docx

# Load model (same as your Flask code)
@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = get_model()

# Same text extraction logic
def extract_text(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return " ".join([page.extract_text() or "" for page in pdf.pages])
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return ""

# UI
st.set_page_config(page_title="Resume Shortlister", layout="centered")

st.title("📄 Resume Shortlister")
st.write("Compare resumes with job description using AI")

# Inputs
jd = st.text_area("Paste Job Description")

resumes = st.file_uploader(
    "Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# Button
if st.button("Analyze"):
    if not jd or not resumes:
        st.warning("Please provide job description and upload resumes")
    else:
        with st.spinner("Analyzing resumes..."):

            jd_embedding = model.encode(jd, convert_to_tensor=True)

            results = []

            for resume in resumes:
                text = extract_text(resume)

                if not text.strip():
                    continue

                resume_embedding = model.encode(text, convert_to_tensor=True)

                score = util.pytorch_cos_sim(jd_embedding, resume_embedding).item()

                results.append({
                    "name": resume.name,
                    "score": round(score * 100, 2)
                })

            results.sort(key=lambda x: x['score'], reverse=True)

        # Output
        st.subheader("📊 Results")

        for r in results:
            st.write(f"**{r['name']}** → {r['score']}%")

        st.dataframe(results)