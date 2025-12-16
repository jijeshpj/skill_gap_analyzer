# ==============================================================================
# Streamlit APP CODE (app.py)
# = ============================================================================

# 1. ആവശ്യമായ ലൈബ്രറികൾ ഇറക്കുമതി ചെയ്യുക
import subprocess
try:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
except:
    pass # ഇൻസ്റ്റാൾ ചെയ്തില്ലെങ്കിൽ മുന്നോട്ട് പോകുക.
import streamlit as st # Streamlit ലൈബ്രറി
import PyPDF2
import spacy
import re
import os
from spacy.matcher import Matcher
# ---------------------------------
# spaCy മോഡൽ ലോഡ് ചെയ്യുന്നു
@st.cache_resource # ഇത് മോഡൽ ഒരേയൊരു തവണ ലോഡ് ചെയ്യാൻ സഹായിക്കുന്നു
def load_model():
    try:
        # നമ്മൾ requirements.txt വഴി ഇൻസ്റ്റാൾ ചെയ്ത മോഡൽ ഉപയോഗിക്കുന്നു
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        st.error("SpaCy model 'en_core_web_sm' could not be loaded.")
        return None

nlp = load_model()
# ---------------------------------
# ---------------------------------
# 2. ടൂൾ സെറ്റപ്പും സ്കിൽ ലിസ്റ്റും (ഗ്ലോബൽ വേരിയബിളുകൾ)
# ---------------------------------
# നിങ്ങളുടെ സ്കിൽ ലിസ്റ്റുകളും മാപ്പിംഗുകളും ഇവിടെ ചേർക്കുക (മുമ്പത്തെ കോഡിൽ നിന്ന് കോപ്പി ചെയ്യുക)
TECH_SKILLS = [
    "python", "java", "sql", "aws", "azure", "docker", "kubernetes", 
    "javascript", "html", "css", "mongodb", "react", "angular", "nlp", 
    "machine learning", "deep learning", "tableau", "power bi", "hadoop", "c++",
    "pandas", "numpy", "data analysis", "cloud computing"
]
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", 
    "time management", "creativity", "adaptability", "mentoring", 
    "management", "agile", "scrum", "public speaking", "presentation"
]

SKILL_MAPPING = {
    'analytical thinking': 'problem solving', 'analytical skills': 'problem solving',
    'data visualization': 'tableau', 'nosql': 'mongodb', 'cloud services': 'aws', 
    'cloud platforms': 'aws', 'deep learning': 'machine learning', 
    'working with team': 'teamwork', 'team player': 'teamwork', 
    'public speaking': 'communication', 'time organizing': 'time management',
    'group projects': 'teamwork', 'business intelligence': 'power bi',
    'cloud computing': 'aws', 'strong communication': 'communication', 
    'presentation skills': 'presentation' 
}

ALL_SKILLS = [s.lower() for s in TECH_SKILLS + SOFT_SKILLS]

# spaCy മോഡൽ ലോഡ് ചെയ്യുന്നു
@st.cache_resource # ഇത് മോഡൽ ഒരേയൊരു തവണ ലോഡ് ചെയ്യാൻ സഹായിക്കുന്നു
def load_model():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        # Streamlit Cloud-ൽ പ്രവർത്തിപ്പിക്കുമ്പോൾ മോഡൽ ഡൗൺലോഡ് ചെയ്യാനുള്ള സാധ്യത
        # Streamlit-ന് ആവശ്യമായ "requirements.txt" ഫയലിലാണ് ഈ മോഡൽ ഉൾപ്പെടുത്തേണ്ടത്.
        st.error("SpaCy model 'en_core_web_sm' not loaded. Check requirements.")
        return None

nlp = load_model()

# ---------------------------------
# 3. ഫംഗ്ഷനുകൾ (Jupyter-ൽ ഉപയോഗിച്ച അതേ ഫംഗ്ഷനുകൾ)
# ---------------------------------

def extract_text_from_pdf(uploaded_file):
    # Streamlit-ൽ ഫയൽ അപ്‌ലോഡ് ചെയ്യുമ്പോൾ ഇത് file buffer ആയിരിക്കും
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def extract_skills_from_text(text, skill_list):
    if not nlp or not text:
        return set()
    
    processed_text = text.lower()
    doc = nlp(processed_text)
    raw_found_skills = set() 
    
    # RAW EXTRACTION ലോജിക്ക്
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if chunk_text in skill_list:
            raw_found_skills.add(chunk_text)
            
    for token in doc:
        token_text = token.text.lower()
        if token_text in skill_list and len(token_text) > 2: 
            raw_found_skills.add(token_text)
            
    for skill in skill_list:
        if len(skill.split()) > 1:
            if skill in processed_text:
                raw_found_skills.add(skill)

    # MAPPING: Synonyms ഉപയോഗിച്ച് മാസ്റ്റർ സ്കില്ലിലേക്ക് മാറ്റുന്നു
    final_mapped_skills = set()
    for skill in raw_found_skills:
        if skill in SKILL_MAPPING: 
            final_mapped_skills.add(SKILL_MAPPING[skill])
        else:
            final_mapped_skills.add(skill)
            
    return final_mapped_skills 

# ---------------------------------
# 5. Comparison Logic: താരതമ്യം ചെയ്യുക (ഇത് app.py-യിൽ ചേർക്കുക)
# ---------------------------------

def compare_skills(resume_skills, required_jd_skills):
    # സെറ്റ് ഓപ്പറേഷനുകൾ ഉപയോഗിച്ച് താരതമ്യം
    matching_skills = resume_skills.intersection(required_jd_skills)
    missing_skills = required_jd_skills.difference(resume_skills)
    extra_skills = resume_skills.difference(required_jd_skills)
    
    return {
        "Matching Skills": matching_skills,
        "Missing Skills": missing_skills,
        "Extra Skills": extra_skills
    }

# ---------------------------------
# 4. STREAMLIT UI/MAIN APP
# ---------------------------------

st.set_page_config(page_title="Skill Gap Analyzer", layout="wide")
st.title("🤖 NLP Skill Gap Analyzer")
st.markdown("Upload a Job Description (TXT) and a Resume (PDF) to get a skill gap report.")

# ഇൻപുട്ട് ഏരിയകൾ
col1, col2 = st.columns(2)

with col1:
    jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
with col2:
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if jd_file and resume_file:
    # JD Text വായിക്കുന്നു (utf-8 ഉപയോഗിക്കുന്നു)
    try:
        jd_text = jd_file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading JD file: {e}")
        jd_text = ""
        
    # Resume Text വായിക്കുന്നു
    resume_text = extract_text_from_pdf(resume_file)

    if jd_text and resume_text:
        with st.spinner("Analyzing skills..."):
            # A. JD Skills
            jd_skills_required = extract_skills_from_text(jd_text, ALL_SKILLS)
            
            # B. Resume Skills
            resume_skills_got = extract_skills_from_text(resume_text, ALL_SKILLS)
            
            # C. Comparison
            gap_report = compare_skills(resume_skills_got, jd_skills_required)

        # -------------------
        # റിപ്പോർട്ട് ഔട്ട്പുട്ട് (Report Output)
        # -------------------
        st.success("✅ Analysis Complete!")
        
        # 1. Summary Metrics
        st.metric(label="Matching Score", value=f"{len(gap_report['Matching Skills'])} / {len(jd_skills_required)}", 
                  delta=f"-{len(gap_report['Missing Skills'])} Missing Skills")

        # 2. Detailed Report
        st.header("Detailed Skill Gap Analysis")

        # Missing Skills
        st.subheader(f"❌ Missing Skills (GAP: {len(gap_report['Missing Skills'])})")
        if gap_report['Missing Skills']:
            st.warning(", ".join(sorted(list(gap_report['Missing Skills']))))
        else:
            st.success("No missing required skills found!")

        # Matching Skills
        st.subheader(f"✔ Matching Skills ({len(gap_report['Matching Skills'])})")
        st.info(", ".join(sorted(list(gap_report['Matching Skills']))))

        # Extra Skills
        st.subheader(f"⭐ Extra Skills (Not required: {len(gap_report['Extra Skills'])})")
        st.code(", ".join(sorted(list(gap_report['Extra Skills']))))

    else:
        st.warning("Please upload valid files to start the analysis.")

# ==============================================================================
