import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os

# Load CSV data
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "ClassRequirements.csv")
df = pd.read_csv(file_path)

# Display data and title
st.title("FIU DEGREE PATHWAY")
st.divider()
#st.write(df)

# Navigation button
if st.button("Degree Audit"):
    st.switch_page("pages/DegreeAudit.py")

def PlotCreditsChart(df):
    df['Completed'] = df['Completed'].str.strip().str.capitalize()

    # Count the Completed Units section
    count_data = df.groupby('Completed')['Credits'].sum().reset_index()
    count_data.columns = ['Marked', 'TotalCredits']

    # Pie chart data
    labels = count_data['Marked']
    sizes = count_data['TotalCredits']

    total_credits = int(sizes.sum())

    # Plot pie chart
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(sizes, startangle=90, wedgeprops=dict(width=0.4), textprops=dict(color="black"))

    ax.text(0, 0, f"{total_credits}\ncredits", ha='center', va='center', fontsize=14, weight='bold')

    custom_labels = [f"{label}: {int(credit)}" for label, credit in zip(labels, sizes)]

    # Add legend (labels on the side)
    ax.legend(wedges, custom_labels, title="Completion Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.axis('equal')  # Equal aspect ratio

    st.pyplot(fig)

PlotCreditsChart(df)

# Normalize column (optional but useful)

    # Divider for visual separation
st.divider()
st.subheader("Enroll In Courses")

# Display Remaining Units
remaining_df = df[df['Completed'].str.lower() == 'remaining units']
in_progress_df = df[df['Completed'].str.lower() == 'in-progress']
planned_df = df[df['Completed'].str.lower() == 'planned']


for idx, row in remaining_df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 2, 2])
    with col1:
        st.write(f"**{row['Course Code']}** - {row['Course Title']} ({row['Credits']} credits)")
    with col2:
        st.write(row['Day'])
    with col3:
        st.write(row['Time'])
    with col4:
        if st.button(f"Enroll", key = f"enroll_btn{idx}"):
            st.success(f"Enrolled in {row['Course Code']}")
            df.at[idx, 'Completed'] = 'In-progress'
            df.to_csv(file_path, index=False) 
            st.rerun()
    with col5:
        if st.button(f"Planner", key = f"planned_btn{idx}"):
            st.success(f"Added course to Planner")
            df.at[idx, 'Completed'] = 'Planned'
            df.to_csv(file_path, index=False)
            st.rerun()

st.divider()
st.subheader("In Progress Courses")

if in_progress_df.empty:
    st.info("No courses currently in progress.")
else:
    for idx, row in in_progress_df.iterrows():
        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])
        with col1:
            st.write(f"**{row['Course Code']}** - {row['Course Title']} ({row['Credits']} credits)")
        with col2:
            st.write(row['Day'])
        with col3:
            st.write(row['Time'])
        with col4:
            if st.button(f"Unenroll", key=f"unenroll_{idx}"):
                st.success(f"Unenrolled in {row['Course Code']}")
                df.at[idx, 'Completed'] = 'Remaining units'
                df.to_csv(file_path, index=False) 
                st.rerun()

st.divider()
if planned_df.empty:
    st.info("No courses currently in progress.")
else:
    for idx, row in planned_df.iterrows():
        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])
        with col1:
            st.write(f"**{row['Course Code']}** - {row['Course Title']} ({row['Credits']} credits)")
        with col2:
            st.write(row['Day'])
        with col3:
            st.write(row['Time'])
        with col4:
            if st.button(f"Remove", key=f"Remove{idx}"):
                st.success(f"Unenrolled in {row['Course Code']}")
                df.at[idx, 'Completed'] = 'Remaining units'
                df.to_csv(file_path, index=False) 
                st.rerun()
