import streamlit as st
import pandas as pd
import os
import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Degree Audit")

# Load the CSV data
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "../ClassRequirements.csv")
df = pd.read_csv(file_path)

# Normalize text
df['Completed'] = df['Completed'].fillna('').str.strip().str.lower()
df['Category'] = df['Category'].fillna('').str.strip()
df['Course Code'] = df['Course Code'].str.strip()
df['Course Title'] = df['Course Title'].str.strip()

# Compute totals for each credit
total_credits = df['Credits'].sum()
completed_credits = df[df['Completed'] == 'completed units']['Credits'].sum()
in_progress_credits = df[df['Completed'] == 'in-progress']['Credits'].sum()
planned_credits = df[df['Completed'] == 'planned']['Credits'].sum()
remaining_credits = df[df['Completed'] == 'remaining units']['Credits'].sum()

# Title for Degree Audit
st.title("Degree Audit")
st.divider()

if st.button("Degree Pathway"):
    st.switch_page("DegreePathway.py")

# Credit summary
st.subheader("Credit Summary")
st.metric("Total Required Credits", total_credits)
st.metric("Completed Credits", completed_credits)
st.metric("In Progress Credits", in_progress_credits)
st.metric("Planned Credits", planned_credits)
st.metric("Remaining Credits", remaining_credits)

st.divider()

# Detailed view
st.subheader("Course Completion Details")

st.write(df)

st.subheader("Estimated Graduation Timeline")

CREDITS_PER_SEMESTER = 12
MONTHS_PER_SEMESTER = 4  # Approx duration of a semester

# Calculate number of semesters remaining (rounded up)
semesters_remaining = -(-remaining_credits // CREDITS_PER_SEMESTER)

# Estimate graduation date
months_until_graduation = semesters_remaining * MONTHS_PER_SEMESTER
estimated_graduation_date = datetime.date.today() + relativedelta(months=months_until_graduation)

# Display result
st.write(f"Based on {CREDITS_PER_SEMESTER} credits/semester, you will likely graduate in **{estimated_graduation_date.strftime('%B %Y')}**.")
