# 1. ആവശ്യമായ ലൈബ്രറികൾ ഇറക്കുമതി ചെയ്യുക
import streamlit as st
# സ്പെയ്uസി, പിഡിഎഫ്, സ്കിൽസ് തുടങ്ങിയ വലിയ ലൈബ്രറികൾ തൽക്കാലം ഒഴിവാക്കുക.

# ---------------------------------
# 2. മിനിമൽ കോൺഫിഗറേഷനും UI-യും
# ---------------------------------

st.set_page_config(page_title="Minimal Test", layout="wide")

st.title("Streamlit Minimal Test Successful!")
st.header("App is Ready.")
st.markdown("If you see this page, the Streamlit Cloud environment is healthy.")

# ടെസ്റ്റ് വിജയകരമായാൽ, ഇവിടെ ഒരു ബട്ടൺ നൽകാം
if st.button("Proceed to Full App Load Test"):
    st.write("Now we can test the full code!")
