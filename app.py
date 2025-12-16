# ==============================================================================
# Streamlit APP CODE (FINAL CLEAN VERSION - app.py)
# ==============================================================================

# 1. ആവശ്യമായ ലൈബ്രറികൾ ഇറക്കുമതി ചെയ്യുക
import streamlit as st
import PyPDF2
import spacy
import os
from spacy.matcher import Matcher # Matcher ഉപയോഗിക്കുന്നില്ലെങ്കിലും ഇമ്പോർട്ട് നിലനിർത്തി

# ---------------------------------
# 2. ടൂൾ സെറ്റപ്പും സ്കിൽ ലിസ്റ്റുകളും
# ---------------------------------
TECH_SKILLS = [
    "python", "java", "sql", "aws", "azure", "docker", "kubernetes", "javascript", 
    "html", "css", "mongodb", "react", "angular", "nlp", "machine learning", 
    "deep learning", "tableau", "power bi", "hadoop", "c++", "pandas", "numpy", 
    "data analysis", "cloud computing"
]
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "time management", 
    "creativity", "adaptability", "mentoring", "management", "agile", "scrum", 
    "public speaking", "presentation"
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

# ---------------------------------
# 3. spaCy മോഡൽ ലോഡിംഗ് (ഒരൊറ്റ തവണ മാത്രം)
# ---------------------------------

@st.cache_resource 
def load_nlp_model():
    """SpaCy മോഡൽ സുരക്ഷിതമായി ലോഡ് ചെയ്യുന്നു."""
    try:
        # requirements.txt വഴി ഇൻസ്റ്റാൾ ചെയ്ത മോഡൽ ഉപയോഗിക്കുന്നു
        nlp = spacy.load("en_core_web_sm") 
        return nlp
    except OSError:
        st.error("❌ SpaCy model 'en_core_web_sm' could not be loaded. Please check requirements.txt.")
        return None

nlp = load_nlp_model() # ഒരു തവണ മാത്രം മോഡൽ ലോഡ് ചെയ്യുന്നു

# ---------------------------------
# 4. ഫംഗ്ഷനുകൾ (Text Extraction, Skill Extraction, Comparison)
# ---------------------------------

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Error reading PDF file: {e}")
        return None

def extract_skills_from_text(text, skill_list):
    if not nlp or not text:
        return set()
        
    processed_text = text.lower()
    doc = nlp(processed_text)
    raw_found_skills = set() 
    
    # RAW EXTRACTION ലോജിക്ക് (Noun Chunks, Tokens, Phrase Matching)
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

def compare_skills(resume_skills, required_jd_skills):
    matching_skills = resume_skills.intersection(required_jd_skills)
    missing_skills = required_jd_skills.difference(resume_skills)
    extra_skills = resume_skills.difference(required_jd_skills)
    
    return {
        "Matching Skills": matching_skills,
        "Missing Skills": missing_skills,
        "Extra Skills": extra_skills
    }

# ---------------------------------
# 5. STREAMLIT UI/MAIN APP
# ---------------------------------

st.set_page_config(page_title="Skill Gap Analyzer", layout="wide")
st.title("🤖 NLP Skill Gap Analyzer")
st.markdown("Upload a Job Description (TXT) and a Resume (PDF) to get a skill gap report.")

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
        st.error(f"❌ Error reading JD file: {e}")
        jd_text = ""
        
    # Resume Text വായിക്കുന്നു
    resume_text = extract_text_from_pdf(resume_file)

    if jd_text and resume_text:
        with st.spinner("Analyzing skills..."):
            jd_skills_required = extract_skills_from_text(jd_text, ALL_SKILLS)
            resume_skills_got = extract_skills_from_text(resume_text, ALL_SKILLS)
            gap_report = compare_skills(resume_skills_got, jd_skills_required)

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
