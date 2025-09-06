import streamlit as st
import matplotlib.pyplot as plt
import io
import textwrap

# --- App title ---
st.markdown(
    """
    <h1 style='text-align: center;'>
        <span style='color: green;'>Focus Work</span>
        <span style='color: gray; font-style: italic'> Planner </span>
        <span style='font-size: 1em;'>⏳</span>
    </h1>
    """,
    unsafe_allow_html=True
)

# --- Config ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Initialize focus_hours in session state
if "focus_hours" not in st.session_state:
    st.session_state.focus_hours = {day: 0 for day in days}

# Initialize selected_day in session state
if "selected_day" not in st.session_state:
    st.session_state.selected_day = days[0]

# Initialize temporary session state variables for task inputs
if "temp_task_name" not in st.session_state:
    st.session_state.temp_task_name = ""
if "temp_duration" not in st.session_state:
    st.session_state.temp_duration = 1
if "temp_color" not in st.session_state:
    st.session_state.temp_color = "#4682B4"

# Calculate max_hours dynamically: if all focus hours are zero, set 12; else take max of focus_hours values.
if all(v == 0 for v in st.session_state.focus_hours.values()):
    max_hours = 12
else:
    max_hours = max(st.session_state.focus_hours.values())

# Storage for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = {day: [] for day in days}
if "editing_day" not in st.session_state:
    st.session_state.editing_day = None
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# --- Task Input ---
with st.expander("Add or Edit Task", expanded=True):
    st.subheader("Add or Edit a Task")
    # Select day (rerun on change)
    day = st.selectbox("Choose a day:", days, index=days.index(st.session_state.selected_day), key="day_select")
    if day != st.session_state.selected_day:
        st.session_state.selected_day = day
        st.session_state.editing_day = None
        st.session_state.editing_index = None
        st.rerun()

    # Editing logic
    if st.session_state.editing_day == day and st.session_state.editing_index is not None:
        task_to_edit = st.session_state.tasks[day][st.session_state.editing_index]
        st.session_state.temp_duration = task_to_edit[0]
        st.session_state.temp_task_name = task_to_edit[1]
        st.session_state.temp_color = task_to_edit[2]

    # Number input for focus hours for the selected day
    focus_hours_val = st.number_input(
        f"{day} Focus Hours:",
        0, 24,
        value=st.session_state.focus_hours.get(day, 0),
        key=f"focus_hours_{day}"
    )
    st.session_state.focus_hours[day] = focus_hours_val
    used = sum(task[0] for task in st.session_state.tasks.get(day, []))
    remaining = focus_hours_val - used
    if st.session_state.tasks.get(day, []):  # only show if there are tasks
        if remaining >= 0:
            st.success(f"Remaining: {remaining}h")
        else:
            st.error(f"Overbooked by {-remaining}h")

    # Task inputs using temp variables
    task_name = st.text_input("Task name:", value=st.session_state.temp_task_name, key=f"task_name_input_{day}")
    duration = st.number_input("Duration (hours):", 1, max_hours, value=st.session_state.temp_duration, key=f"duration_input_{day}")
    color = st.color_picker("Pick a color:", value=st.session_state.temp_color, key=f"color_picker_input_{day}")
    submit_btn = st.button("Add Task" if st.session_state.editing_day is None else "Update Task", key=f"submit_btn_{day}")

    if submit_btn:
        if not task_name:
            st.error("Task name cannot be empty.")
        else:
            if st.session_state.editing_day == day and st.session_state.editing_index is not None:
                st.session_state.tasks[day][st.session_state.editing_index] = (duration, task_name, color)
                st.success(f"Updated {task_name} on {day} ({duration}h)")
            else:
                st.session_state.tasks[day].append((duration, task_name, color))
                st.success(f"Added {task_name} on {day} ({duration}h)")
            # Clear temp variables
            st.session_state.temp_task_name = ""
            st.session_state.temp_duration = 1
            st.session_state.temp_color = "#4682B4"
            st.session_state.editing_day = None
            st.session_state.editing_index = None

            st.rerun()

# --- Tasks List for Selected Day ---
with st.expander(f"Tasks for {st.session_state.selected_day}", expanded=True):
    day = st.session_state.selected_day
    tasks = st.session_state.tasks.get(day, [])
    for idx, (duration, task_name, color) in enumerate(tasks):
        col1, col2, col3 = st.columns([6,1,1])
        with col1:
            st.markdown(f"- {task_name} ({duration}h)")
        with col2:
            if st.button("Edit", key=f"edit_{day}_{idx}", type="primary", width="stretch"):
                st.session_state.editing_day = day
                st.session_state.editing_index = idx
                task_to_edit = st.session_state.tasks[day][idx]
                st.session_state.temp_duration = task_to_edit[0]
                st.session_state.temp_task_name = task_to_edit[1]
                st.session_state.temp_color = task_to_edit[2]
                st.rerun()
        with col3:
            if st.button("Del", key=f"delete_{day}_{idx}", type="secondary", width="stretch"):
                st.session_state.tasks[day].pop(idx)
                if st.session_state.editing_day == day and st.session_state.editing_index == idx:
                    st.session_state.editing_day = None
                    st.session_state.editing_index = None
                    st.session_state.temp_task_name = ""
                    st.session_state.temp_duration = 1
                    st.session_state.temp_color = "#4682B4"
                st.rerun()

# --- Plot Schedule ---
with st.container():
    st.write(
        "📊 **Weekly Schedule Chart:** On mobile, scroll horizontally to view all hours."
    )
    fig, ax = plt.subplots(figsize=(18, 7))
    fig.patch.set_facecolor("#111111")  # GSAP inspired dark background
    ax.set_facecolor("#1E1E1E")
    ax.tick_params(colors="white")
    ax.set_xlabel("Hours", fontsize=13, fontweight="bold", color="white")
    ax.set_ylabel("")
    ax.set_title("Weekly Focus Schedule", fontsize=16, fontweight="bold", pad=20, color="white")
    for spine in ax.spines.values():
        spine.set_color("#39FF14")
        spine.set_linewidth(1.2)
    ax.grid(axis="x", linestyle="--", alpha=0.3, color="white")

    for i, day in enumerate(days):
        allocated = st.session_state.focus_hours.get(day, 0)
        tasks = st.session_state.tasks.get(day, [])
        used = sum(task[0] for task in tasks)
        cumulative_start = 0
        for duration, label, color in tasks:
            if used > allocated:
                facecolor = "#FF9999"
                edgecolor = color
                linewidth = 2
            else:
                facecolor = color
                edgecolor = "black"
                linewidth = 1
            # Rounded bar edges
            bar = ax.barh(
                y=i, width=duration, left=cumulative_start, height=0.6,
                color=facecolor, edgecolor=edgecolor, linewidth=linewidth
            )
            # Add value label inside bar
            full_label = f"{label} ({duration}h)"
            wrapped_label = textwrap.fill(full_label, width=50)
            ax.text(
                cumulative_start + duration/2, i,
                wrapped_label,
                ha="center", va="center", color="white",
                fontsize=12, fontweight="bold"
            )
            cumulative_start += duration

        # Show allocated hours as a faint bar behind tasks
        if allocated > 0:
            ax.barh(
                y=i, width=allocated, left=0, height=0.6,
                color="#e0e0e0", edgecolor="none", zorder=0
            )

    ax.set_yticks(range(len(days)))
    ax.set_yticklabels(days, fontsize=13, fontweight="bold", color="white")
    ax.set_xticks(range(0, max_hours+1))
    ax.set_xlim(0, max_hours)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    st.pyplot(fig)

    # Export figure as PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(
        label="Download Schedule as PNG",
        data=buf,
        file_name="my_focus_schedule.png",
        mime="image/png"
    )

# --- Reset button ---
if st.button("Reset Schedule"):
    st.session_state.tasks = {day: [] for day in days}
    st.session_state.focus_hours = {day: 0 for day in days}
    st.session_state.selected_day = days[0]
    st.session_state.editing_day = None
    st.session_state.editing_index = None
    st.session_state.temp_task_name = ""
    st.session_state.temp_duration = 1
    st.session_state.temp_color = "#4682B4"
    st.rerun()