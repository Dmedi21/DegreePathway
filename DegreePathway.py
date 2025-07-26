import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
import datetime
from dateutil.relativedelta import relativedelta

# Load CSV data
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "ClassRequirements.csv")
df = pd.read_csv(file_path)

#Gets record of which courses are completed
df['Completed'] = df['Completed'].fillna('').str.strip().str.lower()
completed_courses = set(df[df['Completed'] == 'Completed units']['Course Code'].str.strip())

#Default filter settings for when clear filters is pressed
def default_filter():
    st.session_state["search_bar"] = ""
    st.session_state["selected_days"] = []
    st.session_state["selected_category"] = []
    st.session_state["selected_time"] = []

#This is just to spilt up the days options so in the filters, it is not listed as Monday, Wednesday
day_options = set()
df['Day'] = df['Day'].fillna('')
for entry in df['Day']:
    split_days = [d.strip() for d in entry.split(',')]
    day_options.update(split_days)


#Shows the options for days in this order
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Online"]
day_options = [day for day in day_order if day in day_options]

#Shows the options for time in this order
time_order = ["10AM - 11:30AM", "12PM - 2:30PM", "3PM - 6PM", "TBA"]
time_options = [time for time in time_order if time in time_order]

# Displays title
st.title("FIU DEGREE PATHWAY")
st.divider()


# Button to open Degree Audit
if st.button("Degree Audit"):
    st.switch_page("pages/DegreeAudit")

# Estimate Graduation Date
st.subheader("Estimated Graduation Date")

CREDITS_PER_SEMESTER = 12
MONTHS_PER_SEMESTER = 4  # Approx duration of a semester

# Calculate number of semesters remaining (rounded up)
remaining_credits = df[df['Completed'] == 'remaining units']['Credits'].sum()
semesters_remaining = -(-remaining_credits // CREDITS_PER_SEMESTER)

# Estimate graduation date
months_until_graduation = semesters_remaining * MONTHS_PER_SEMESTER
estimated_graduation_date = datetime.date.today() + relativedelta(months=months_until_graduation)

# Display result
st.write(f"Based on {CREDITS_PER_SEMESTER} credits/semester, you will likely graduate in **{estimated_graduation_date.strftime('%B %Y')}**.")

# Defined method that creates the chart showing Completion status
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

# Called automatically when page opens
PlotCreditsChart(df)


st.divider()


st.subheader("Enroll In Courses")

# Search bar
search_bar = st.text_input("Search for a course: ", key = "search_bar").strip().lower()


# Sees what in the data is considered remaining, in-progress, and planned
remaining_df = df[df['Completed'].str.lower() == 'remaining units']
in_progress_df = df[df['Completed'].str.lower() == 'in-progress']
planned_df = df[df['Completed'].str.lower() == 'planned']

# Filter
with st.expander("Filter"):
    st.button("Clear Filters", on_click = default_filter)
    selected_category = st.multiselect("Filter by Category", options = remaining_df['Category'].dropna().unique(), key = "selected_category")
    selected_days = st.multiselect("Filter by Day", options = day_options, key = "selected_days")
    selected_time = st.multiselect("Filter by Time", options = time_options, key = "selected_time")

# Logic to show classes that are searched on the search bar. Only looks at Course Title and Course Code
if search_bar:
    search_bar = str(search_bar)
    query = st.session_state.search_bar.strip().lower()
    filtered_remaining_df = remaining_df[remaining_df['Course Code'].str.lower().str.contains(query) | remaining_df['Course Title'].str.lower().str.contains(query)]
else:
    filtered_remaining_df = remaining_df

# Filters based on Category
if st.session_state.selected_category:
    filtered_remaining_df = filtered_remaining_df[filtered_remaining_df['Category'].isin(selected_category)]

# Filters based on Days
if st.session_state.selected_days:
    filtered_remaining_df = filtered_remaining_df[filtered_remaining_df['Day'].apply(lambda d: any(day in [part.strip() for part in d.split(',')] for day in selected_days))]

# Filters based on Time
if st.session_state.selected_time:
    filtered_remaining_df = filtered_remaining_df[filtered_remaining_df["Time"].isin(selected_time)]

if st.button("Recommend Courses"):
    # Identify completed courses
    completed_courses = df[df['Completed'].str.lower() == "completed units"]['Course Code'].str.strip().tolist()
    
    # Filter recommended and not already enrolled/planned/completed
    eligible_df = df[
        (df['Recommended'].str.strip().str.lower() == "yes")
    ]

    # Filter by prerequisite satisfaction
    def prereq_met(row):
        prereq = str(row['Pre-requisite']).strip()
        return not prereq or prereq in completed_courses

    eligible_df = eligible_df[eligible_df.apply(prereq_met, axis=1)]

    # Pick up to 4 recommended courses
    recommended_courses = eligible_df.sample(n=min(4, len(eligible_df)), random_state=42)

    if recommended_courses.empty:
        st.warning("No eligible recommended courses available at this time.")
    else:
        for idx in recommended_courses.index:
            df.at[idx, 'Completed'] = 'In-progress'
        df.to_csv(file_path, index=False)
        st.success(f"Enrolled in {len(recommended_courses)} recommended courses.")
        st.rerun()

# List of classes to Enroll in/Plan for.
for idx, row in filtered_remaining_df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 2, 2])
    # Course Code, Title, and Credits displayed
    with col1:
        st.write(f"**{row['Course Code']}** - {row['Course Title']} ({row['Credits']} credits)")
    # Day displayed
    with col2:
        st.write(row['Day'])
    # Time displayed
    with col3:
        st.write(row['Time'])
    
    # Logic to check the pre-requisite for the class so the software can see if the user has met the conditions to enroll
    prereq = row['Pre-requisite']
    has_prereq = isinstance(prereq, str) and prereq.strip() != ""
    prereq_done = (not has_prereq) or (prereq.strip() in completed_courses)

    # Allows user to enroll for class if they met the pre-requisite. If they didn't, the software tells them the pre-requisite they need
    with col4:
        if prereq_done:
            if st.button(f"Enroll", key = f"enroll_btn{idx}"):
                st.success(f"Enrolled in {row['Course Code']}")
                df.at[idx, 'Completed'] = 'In-progress'
                df.to_csv(file_path, index=False) 
                st.rerun()
        else:
            st.button(f"Enroll", key = f"enroll_btn_disabled_{idx}", disabled = True)
            st.caption(f"Pre-requisite has not been met: {prereq.strip()}")
    # Allows user to add class to their planner. Does not matter is pre-requisite is met or not.
    with col5:
        if st.button(f"Planner", key = f"planned_btn{idx}"):
            st.success(f"Added course to Planner")
            df.at[idx, 'Completed'] = 'Planned'
            df.to_csv(file_path, index=False)
            st.rerun()

#List of classes the student is enrolled in
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

#List of classes that are in the planner
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
