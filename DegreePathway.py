import streamlit as st

st.title("FIU DEGREE PATHWAY")
if st.button("Degree Audit"):
    st.switch_page("pages/DegreeAudit.py")
