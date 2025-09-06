import streamlit as st
import matplotlib.pyplot as plt

# --- App title ---
st.title("Weekly Schedule Planner")

# --- Config ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Choose time scale
time_scale = st.radio("Select time scale:", ["12 hours", "24 hours"])
max_hours = 12 if time_scale == "12 hours" else 24

# Storage for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = {day: [] for day in days}
if "editing_day" not in st.session_state:
    st.session_state.editing_day = None
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# --- Task Input ---
with st.form("task_form"):
    if st.session_state.editing_day is not None and st.session_state.editing_index is not None:
        day = st.selectbox("Choose a day:", days, index=days.index(st.session_state.editing_day))
        task_to_edit = st.session_state.tasks[st.session_state.editing_day][st.session_state.editing_index]
        task_name_default = task_to_edit[2]
        duration_default = task_to_edit[1]
        start_default = task_to_edit[0]
        color_default = task_to_edit[3]
    else:
        day = st.selectbox("Choose a day:", days)
        task_name_default = ""
        duration_default = 1
        start_default = 0
        color_default = "#4682B4"

    task_name = st.text_input("Task name:", value=task_name_default)
    duration = st.number_input("Duration (hours):", 1, max_hours, value=duration_default)
    start = st.number_input("Start time (hour):", 0, max_hours-1, value=start_default)
    color = st.color_picker("Pick a color:", color_default)
    submitted = st.form_submit_button("Add Task" if st.session_state.editing_day is None else "Update Task")

    if submitted and task_name:
        if st.session_state.editing_day is not None and st.session_state.editing_index is not None:
            st.session_state.tasks[st.session_state.editing_day][st.session_state.editing_index] = (start, duration, task_name, color)
            st.success(f"Updated {task_name} on {day} ({duration}h)")
            st.session_state.editing_day = None
            st.session_state.editing_index = None
        else:
            st.session_state.tasks[day].append((start, duration, task_name, color))
            st.success(f"Added {task_name} on {day} ({duration}h)")

# --- Manage Tasks ---
st.header("Manage Tasks")
for day in days:
    st.subheader(day)
    tasks = st.session_state.tasks.get(day, [])
    for idx, (start, duration, task_name, color) in enumerate(tasks):
        col1, col2, col3 = st.columns([6,1,1])
        with col1:
            checked = st.checkbox(f"{task_name} ({duration}h)", key=f"{day}_{idx}")
        with col2:
            if st.button("Edit", key=f"edit_{day}_{idx}"):
                st.session_state.editing_day = day
                st.session_state.editing_index = idx
                st.experimental_rerun()
        with col3:
            if st.button("Delete", key=f"delete_{day}_{idx}"):
                st.session_state.tasks[day].pop(idx)
                st.experimental_rerun()

# --- Plot Schedule ---
fig, ax = plt.subplots(figsize=(12, 6))

for i, day in enumerate(days):
    for start, duration, label, color in st.session_state.tasks.get(day, []):
        ax.barh(y=i, width=duration, left=start, height=0.6, color=color, edgecolor="black")
        ax.text(start + duration/2, i, f"{label} ({duration}h)",
                ha="center", va="center", color="white", fontsize=9, fontweight="bold")

ax.set_yticks(range(len(days)))
ax.set_yticklabels(days)
ax.set_xticks(range(0, max_hours+1))
ax.set_xlim(0, max_hours)
ax.set_xlabel("Hours")
ax.set_title("Weekly Schedule")
ax.invert_yaxis()
st.pyplot(fig)

# --- Reset button ---
if st.button("Reset Schedule"):
    st.session_state.tasks = {day: [] for day in days}
    st.experimental_rerun()