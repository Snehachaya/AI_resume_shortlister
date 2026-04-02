import streamlit as st
from supabase import create_client
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import docx

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Resume Shortlister", layout="wide")

# -------------------- SUPABASE --------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- AUTH FUNCTIONS --------------------
def signup(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def login(email, password):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except:
        return None

# -------------------- SESSION --------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------- LOGIN UI --------------------
menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

if not st.session_state.user:

    st.title("🔐 Resume Shortlister Login")

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = login(email, password)
            if res and res.user:
                st.session_state.user = res.user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    elif choice == "Signup":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Signup"):
            res = signup(email, password)

            if res and res.user:
                st.success("Account created! Please login.")
            else:
                st.error("Signup failed. Check details or email may already exist.")
    st.stop()

# -------------------- LOGOUT --------------------
st.sidebar.write(f"👤 {st.session_state.user.email}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# -------------------- MODEL --------------------
@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = get_model()

# -------------------- FILE TEXT EXTRACTION --------------------
def extract_text(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return " ".join([page.extract_text() or "" for page in pdf.pages])
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return ""

# -------------------- MAIN APP --------------------
st.title("📄 Resume Shortlister")
st.info("📱 Mobile users: upload one file at a time")

jd = st.text_area("Paste Job Description")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF/DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# Mobile fix
if uploaded_files and not isinstance(uploaded_files, list):
    uploaded_files = [uploaded_files]

# -------------------- ANALYZE --------------------
if st.button("Analyze"):
    if not jd or not uploaded_files:
        st.warning("Please provide job description and upload resumes")
    else:
        with st.spinner("Analyzing resumes..."):

            jd_embedding = model.encode(jd, convert_to_tensor=True)
            results = []

            for file in uploaded_files:
                text = extract_text(file)

                if not text.strip():
                    continue

                resume_embedding = model.encode(text, convert_to_tensor=True)
                score = util.pytorch_cos_sim(jd_embedding, resume_embedding).item()

                results.append({
                    "name": file.name,
                    "score": round(score * 100, 2)
                })

            results.sort(key=lambda x: x['score'], reverse=True)

        # -------------------- RESULTS --------------------
        st.subheader("📊 Results")

        top = results[0]
        st.success(f"🏆 Top Candidate: {top['name']} ({top['score']}%)")

        st.dataframe(results)

        # Download CSV
        import pandas as pd
        df = pd.DataFrame(results)
        st.download_button("📥 Download Results", df.to_csv(index=False), "results.csv")