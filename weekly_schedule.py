import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import textwrap
import re

# --- App title ---
st.markdown(
    """
    <h1 style='text-align: center;'>
        <span style='color: #39FF14;'>Focus Work</span>
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

# Initialize form clearing flag
if "clear_form" not in st.session_state:
    st.session_state.clear_form = False

# Calculate max_hours dynamically: if all focus hours are zero, set 12; else take max of focus_hours values.
if all(v == 0 for v in st.session_state.focus_hours.values()):
    max_hours = 12
else:
    max_hours = max(st.session_state.focus_hours.values())

# Initialize goal-color mapping and color palette
if "goal_colors" not in st.session_state:
    st.session_state.goal_colors = {}

if "color_palette" not in st.session_state:
    # Curated color palette that looks good together
    st.session_state.color_palette = [
        "#4A90E2",  # Blue
        "#7ED321",  # Green  
        "#F5A623",  # Orange
        "#D0021B",  # Red
        "#9013FE",  # Purple
        "#50E3C2",  # Teal
        "#B8E986",  # Light Green
        "#FF6B6B",  # Coral
        "#4ECDC4",  # Mint
        "#45B7D1",  # Sky Blue
        "#96CEB4",  # Sage
        "#FFEAA7",  # Yellow
        "#DDA0DD",  # Plum
        "#87CEEB",  # Light Blue
        "#F0A591"   # Peach
    ]

def get_goal_color(task_name):
    """Get color for a goal using fuzzy matching"""
    
    # Clean and normalize the task name for matching
    clean_task = re.sub(r'[^\w\s]', '', task_name.lower().strip())
    clean_words = set(clean_task.split())
    
    # Check existing goals for fuzzy match
    for existing_goal, color in st.session_state.goal_colors.items():
        clean_existing = re.sub(r'[^\w\s]', '', existing_goal.lower().strip())
        existing_words = set(clean_existing.split())
        
        # If they share significant words, consider it a match
        if clean_words and existing_words:
            overlap = len(clean_words.intersection(existing_words))
            min_words = min(len(clean_words), len(existing_words))
            
            # Match if at least 60% of words overlap or exact substring match
            if (overlap / min_words >= 0.6) or (clean_task in clean_existing) or (clean_existing in clean_task):
                return color
    
    # No match found, assign new color
    color_index = len(st.session_state.goal_colors) % len(st.session_state.color_palette)
    new_color = st.session_state.color_palette[color_index]
    st.session_state.goal_colors[task_name] = new_color
    return new_color

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
        st.session_state.clear_form = True
        st.rerun()

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

    # Determine default values for form fields
    if st.session_state.editing_day == day and st.session_state.editing_index is not None:
        # Editing mode - use task values
        task_to_edit = st.session_state.tasks[day][st.session_state.editing_index]
        default_duration = task_to_edit[0]
        default_task_name = task_to_edit[1]
        default_color = task_to_edit[2]
    elif st.session_state.clear_form:
        # Clear form after submit or day change
        default_duration = 1
        default_task_name = ""
        default_color = st.session_state.color_palette[0]  # First color as default
        st.session_state.clear_form = False
    else:
        # Normal mode - keep current values or defaults
        default_duration = 1
        default_task_name = ""
        default_color = st.session_state.color_palette[0]  # First color as default

    # Task inputs wrapped in form to prevent accidental submissions
    with st.form(key=f"task_form_{day}_{st.session_state.get('form_key', 0)}"):
        task_name = st.text_input("Task name:", value=default_task_name)
        duration = st.number_input("Duration (hours):", 1, max_hours, value=default_duration)
        
        # Auto-suggest color based on task name
        if task_name and task_name.strip():
            suggested_color = get_goal_color(task_name)
        else:
            suggested_color = st.session_state.color_palette[0]
        
        color = st.color_picker("Pick a color (Optional):", value=suggested_color)
        
        # Show matching info
        if task_name and task_name.strip():
            matched_goal = None
            clean_task = re.sub(r'[^\w\s]', '', task_name.lower().strip())
            clean_words = set(clean_task.split())
            
            for existing_goal in st.session_state.goal_colors.keys():
                clean_existing = re.sub(r'[^\w\s]', '', existing_goal.lower().strip())
                existing_words = set(clean_existing.split())
                
                if clean_words and existing_words:
                    overlap = len(clean_words.intersection(existing_words))
                    min_words = min(len(clean_words), len(existing_words))
                    
                    if (overlap / min_words >= 0.6) or (clean_task in clean_existing) or (clean_existing in clean_task):
                        if existing_goal != task_name:  # Only show if it's different
                            matched_goal = existing_goal
                        break
            
            if matched_goal:
                st.info(f"💡 Matched with existing goal: '{matched_goal}'")
            elif task_name.strip() not in st.session_state.goal_colors:
                st.success(f"✨ New goal detected - assigned fresh color")
        
        submit_btn = st.form_submit_button("Add Task" if st.session_state.editing_day is None else "Update Task")

        if submit_btn:
            if not task_name:
                st.error("Task name cannot be empty.")
            else:
                # Use the actual color from the picker, but update the goal mapping
                final_color = color
                if task_name.strip():
                    st.session_state.goal_colors[task_name] = final_color
                    
                if st.session_state.editing_day == day and st.session_state.editing_index is not None:
                    st.session_state.tasks[day][st.session_state.editing_index] = (duration, task_name, final_color)
                    st.success(f"Updated {task_name} on {day} ({duration}h)")
                else:
                    st.session_state.tasks[day].append((duration, task_name, final_color))
                    st.success(f"Added {task_name} on {day} ({duration}h)")
                
                # Clear form after submit
                st.session_state.editing_day = None
                st.session_state.editing_index = None
                st.session_state.clear_form = True
                # Increment form key to force widget recreation
                if "form_key" not in st.session_state:
                    st.session_state.form_key = 0
                st.session_state.form_key += 1
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
                st.session_state.clear_form = False
                # Increment form key to force widget recreation with new values
                if "form_key" not in st.session_state:
                    st.session_state.form_key = 0
                st.session_state.form_key += 1
                st.rerun()
        with col3:
            if st.button("Del", key=f"delete_{day}_{idx}", type="secondary", width="stretch"):
                st.session_state.tasks[day].pop(idx)
                if st.session_state.editing_day == day and st.session_state.editing_index == idx:
                    st.session_state.editing_day = None
                    st.session_state.editing_index = None
                    st.session_state.clear_form = True
                    if "form_key" not in st.session_state:
                        st.session_state.form_key = 0
                    st.session_state.form_key += 1
                st.rerun()

# --- Copy Shortcuts ---
if st.session_state.tasks.get(st.session_state.selected_day, []):  # Only show if current day has tasks
    with st.expander("📋 Copy Tasks to Other Days", expanded=False):
        st.subheader(f"Copy from {st.session_state.selected_day}")
        
        # Show current day's tasks with selection
        current_tasks = st.session_state.tasks[st.session_state.selected_day]
        st.write(f"**Select tasks to copy:**")
        
        # Create checkboxes for each task
        selected_tasks = []
        for idx, (duration, task_name, color) in enumerate(current_tasks):
            if st.checkbox(f"{task_name} ({duration}h)", key=f"copy_task_{idx}", value=True):
                selected_tasks.append((duration, task_name, color))
        
        if not selected_tasks:
            st.warning("⚠️ Select at least one task to copy.")
            st.stop()  # Don't show copy options if no tasks selected
        
        st.write("---")
        
        # Copy options in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Quick Copy Options:**")
            
            if st.button("📅 Copy to All Weekdays (Mon-Fri)", use_container_width=True):
                weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                copy_count = 0
                for target_day in weekdays:
                    if target_day != st.session_state.selected_day:
                        # Copy tasks and update focus hours
                        st.session_state.tasks[target_day] = selected_tasks.copy()
                        total_hours = sum(task[0] for task in selected_tasks)
                        st.session_state.focus_hours[target_day] = total_hours
                        copy_count += 1
                
                if copy_count > 0:
                    st.success(f"✅ Copied to {copy_count} weekdays!")
                    st.rerun()
            
            if st.button("📆 Copy to Entire Week", use_container_width=True):
                copy_count = 0
                for target_day in days:
                    if target_day != st.session_state.selected_day:
                        # Copy tasks and update focus hours
                        st.session_state.tasks[target_day] = selected_tasks.copy()
                        total_hours = sum(task[0] for task in selected_tasks)
                        st.session_state.focus_hours[target_day] = total_hours
                        copy_count += 1
                
                if copy_count > 0:
                    st.success(f"✅ Copied to all {copy_count} days!")
                    st.rerun()
        
        with col2:
            st.write("**Select Specific Days:**")
            
            # Multi-select for specific days
            available_days = [day for day in days if day != st.session_state.selected_day]
            selected_days = st.multiselect(
                "Choose days to copy to:",
                available_days,
                key="copy_target_days"
            )
            
            if selected_days and st.button("📝 Copy to Selected Days", use_container_width=True):
                for target_day in selected_days:
                    # Copy tasks and update focus hours
                    st.session_state.tasks[target_day] = selected_tasks.copy()
                    total_hours = sum(task[0] for task in selected_tasks)
                    st.session_state.focus_hours[target_day] = total_hours
                
                st.success(f"✅ Copied to: {', '.join(selected_days)}!")
                st.rerun()
        
        st.write("---")
        
        # Warning section
        st.warning("""
        ⚠️ **Note:** Copying will replace all existing tasks and focus hours on target days.
        """)
        
        # Advanced options
        with st.expander("⚙️ Advanced Copy Options", expanded=False):
            st.write("**Copy Mode:**")
            copy_mode = st.radio(
                "How should copying work?",
                ["Replace all tasks", "Add to existing tasks"],
                key="copy_mode"
            )
            
            st.write("**Focus Hours:**")
            focus_mode = st.radio(
                "How should focus hours be handled?",
                ["Auto-calculate from copied tasks", "Keep existing focus hours", "Add to existing focus hours"],
                key="focus_mode"
            )
            
            # Custom copy with advanced options
            if st.button("🔧 Copy with Advanced Settings", use_container_width=True):
                if selected_days:
                    for target_day in selected_days:
                        if copy_mode == "Replace all tasks":
                            st.session_state.tasks[target_day] = selected_tasks.copy()
                        else:  # Add to existing
                            existing_tasks = st.session_state.tasks.get(target_day, [])
                            st.session_state.tasks[target_day] = existing_tasks + selected_tasks.copy()
                        
                        # Handle focus hours based on mode
                        copied_hours = sum(task[0] for task in selected_tasks)
                        if focus_mode == "Auto-calculate from copied tasks":
                            if copy_mode == "Replace all tasks":
                                st.session_state.focus_hours[target_day] = copied_hours
                            else:  # Add to existing
                                existing_focus = st.session_state.focus_hours.get(target_day, 0)
                                st.session_state.focus_hours[target_day] = existing_focus + copied_hours
                        elif focus_mode == "Add to existing focus hours":
                            existing_focus = st.session_state.focus_hours.get(target_day, 0)
                            st.session_state.focus_hours[target_day] = existing_focus + copied_hours
                        # "Keep existing focus hours" does nothing
                    
                    mode_text = "replaced" if copy_mode == "Replace all tasks" else "added to"
                    st.success(f"✅ Tasks {mode_text} {', '.join(selected_days)} with advanced settings!")
                    st.rerun()
                else:
                    st.error("Please select at least one day to copy to.")

# --- Plot Schedule ---
with st.container():
    st.markdown("""
    <div style='text-align: center; margin: 30px 0;'>
        <h2 style='color: #39FF14; font-weight: 900; font-size: 2.2em; margin-bottom: 10px;'>
            📊 Weekly Focus Schedule
        </h2>
        <p style='color: #888; font-size: 1.1em; margin: 0;'>
            Swipe horizontally on mobile to view all hours
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(20, 8))
    
    # Bold dark theme
    fig.patch.set_facecolor("#0A0A0A")
    ax.set_facecolor("#1A1A1A")
    
    # Modern styling
    ax.tick_params(colors="#FFFFFF", labelsize=12, width=2, length=6)
    ax.set_xlabel("Hours", fontsize=16, fontweight="bold", color="#39FF14", labelpad=15)
    ax.set_ylabel("")
    
    # Bold grid
    ax.grid(axis="x", linestyle="-", alpha=0.2, color="#39FF14", linewidth=1.5)
    ax.grid(axis="y", linestyle="--", alpha=0.1, color="#666666", linewidth=1)
    
    # Neon border styling
    for spine in ax.spines.values():
        spine.set_color("#39FF14")
        spine.set_linewidth(3)
    
    # Hide top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for i, day in enumerate(days):
        allocated = st.session_state.focus_hours.get(day, 0)
        tasks = st.session_state.tasks.get(day, [])
        used = sum(task[0] for task in tasks)
        
        # Background allocated hours bar with gradient effect
        if allocated > 0:
            bg_bar = ax.barh(
                y=i, width=allocated, left=0, height=0.7,
                color="#2A2A2A", edgecolor="#444444", linewidth=2,
                alpha=0.6, zorder=1
            )
        
        cumulative_start = 0
        for j, (duration, label, color) in enumerate(tasks):
            # Bold color scheme
            if used > allocated:
                facecolor = "#FF4444"  # Bright red for overbooked
                edgecolor = "#FFFFFF"
                linewidth = 3
                alpha = 0.9
            else:
                # Make colors more vibrant
                rgb = mcolors.hex2color(color)
                # Increase saturation
                hsv = mcolors.rgb_to_hsv(rgb)
                hsv[1] = min(1.0, hsv[1] * 1.0)  # Boost saturation
                hsv[2] = min(1.0, hsv[2] * 1.1)  # Slight brightness boost
                vibrant_color = mcolors.hsv_to_rgb(hsv)
                facecolor = vibrant_color
                edgecolor = "#FFFFFF"
                linewidth = 2
                alpha = 0.95
            
            # Create bar with rounded corners effect
            bar = ax.barh(
                y=i, width=duration, left=cumulative_start, height=0.7,
                color=facecolor, edgecolor=edgecolor, linewidth=linewidth,
                alpha=alpha, zorder=2
            )
            
            # Bold text styling
            full_label = f"{label}\n({duration}h)"
            wrapped_label = textwrap.fill(full_label, width=35)
            
            # Add shadow effect to text
            shadow_offset = 0.02
            ax.text(
                cumulative_start + duration/2 + shadow_offset, i - shadow_offset,
                wrapped_label,
                ha="center", va="center", color="#000000",
                fontsize=14, fontweight="bold", alpha=0, zorder=3, backgroundcolor="#00000022"
            )
            
            # Main text
            text_color = "#FFFFFF" if sum(mcolors.hex2color(color))/3 < 0.5 else "#000000"
            ax.text(
                cumulative_start + duration/2, i,
                wrapped_label,
                ha="center", va="center", color=text_color,
                fontsize=14, fontweight="900", zorder=4, backgroundcolor="#00000022"
            )
            cumulative_start += duration

    # Bold day labels
    ax.set_yticks(range(len(days)))
    ax.set_yticklabels([f"💪 {day}" for day in days], fontsize=14, fontweight="bold", color="#FFFFFF")
    
    # Bold hour markers
    ax.set_xticks(range(0, max_hours+1, 2))  # Every 2 hours for cleaner look
    ax.set_xlim(0, max_hours)
    ax.invert_yaxis()
    
    # Add subtle background pattern
    for i in range(len(days)):
        if i % 2 == 0:
            ax.axhspan(i-0.4, i+0.4, alpha=0.05, color="#39FF14", zorder=0)

    plt.tight_layout(pad=2.0)
    st.pyplot(fig, use_container_width=True)

    # Bold download section
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Export complete section as PNG including heading
        buf = io.BytesIO()
        
        # Create new figure with heading - increased height for proper spacing
        complete_fig = plt.figure(figsize=(25, 12))
        complete_fig.patch.set_facecolor("#0A0A0A")
        
        # Add title at top with more space
        complete_fig.suptitle("Weekly Focus Schedule", 
                            fontsize=28, fontweight='bold', color='#39FF14', y=0.95)
        
        # Create subplot for the main chart - moved down to give title more room
        ax = complete_fig.add_subplot(111)
        ax.set_position([0.08, 0.08, 0.85, 0.8])  # [left, bottom, width, height]
        
        # Copy all the chart styling
        ax.set_facecolor("#1A1A1A")
        ax.tick_params(colors="#FFFFFF", labelsize=12, width=2, length=6)
        ax.set_xlabel("Hours", fontsize=16, fontweight="bold", color="#39FF14", labelpad=15)
        ax.set_ylabel("")
        ax.grid(axis="x", linestyle="-", alpha=0.2, color="#39FF14", linewidth=1.5)
        ax.grid(axis="y", linestyle="--", alpha=0.1, color="#666666", linewidth=1)
        
        for spine in ax.spines.values():
            spine.set_color("#39FF14")
            spine.set_linewidth(3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Recreate all the bars and data
        for i, day in enumerate(days):
            allocated = st.session_state.focus_hours.get(day, 0)
            tasks = st.session_state.tasks.get(day, [])
            used = sum(task[0] for task in tasks)
            
            if allocated > 0:
                ax.barh(y=i, width=allocated, left=0, height=0.7,
                       color="#2A2A2A", edgecolor="#444444", linewidth=2,
                       alpha=0.6, zorder=1)
            
            cumulative_start = 0
            for j, (duration, label, color) in enumerate(tasks):
                if used > allocated:
                    facecolor = "#FF4444"
                    edgecolor = "#FFFFFF"
                    linewidth = 3
                    alpha = 0.9
                else:
                    rgb = mcolors.hex2color(color)
                    hsv = mcolors.rgb_to_hsv(rgb)
                    hsv[1] = min(1.0, hsv[1] * 1.4)
                    hsv[2] = min(1.0, hsv[2] * 1.1)
                    vibrant_color = mcolors.hsv_to_rgb(hsv)
                    facecolor = vibrant_color
                    edgecolor = "#FFFFFF"
                    linewidth = 2
                    alpha = 0.95
                
                ax.barh(y=i, width=duration, left=cumulative_start, height=0.7,
                       color=facecolor, edgecolor=edgecolor, linewidth=linewidth,
                       alpha=alpha, zorder=2)
                
                full_label = f"{label}\n({duration}h)"
                wrapped_label = textwrap.fill(full_label, width=35)
                
                shadow_offset = 0.02
                ax.text(cumulative_start + duration/2 + shadow_offset, i - shadow_offset,
                       wrapped_label, ha="center", va="center", color="#000000",
                       fontsize=14, fontweight="bold", alpha=0, zorder=3, backgroundcolor="#00000022")
                
                text_color = "#FFFFFF" if sum(mcolors.hex2color(color))/3 < 0.5 else "#000000"
                ax.text(cumulative_start + duration/2, i, wrapped_label,
                       ha="center", va="center", color=text_color,
                       fontsize=14, fontweight="900", zorder=4, backgroundcolor="#00000022")
                cumulative_start += duration

        ax.set_yticks(range(len(days)))
        ax.set_yticklabels([f"💪 {day}" for day in days], fontsize=14, fontweight="bold", color="#FFFFFF")
        ax.set_xticks(range(0, max_hours+1, 2))
        ax.set_xlim(0, max_hours)
        ax.invert_yaxis()
        
        for i in range(len(days)):
            if i % 2 == 0:
                ax.axhspan(i-0.4, i+0.4, alpha=0.05, color="#39FF14", zorder=0)
        
        complete_fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', 
                           facecolor="#0A0A0A", edgecolor='none')
        buf.seek(0)
        plt.close(complete_fig)  # Close to free memory
        
        st.download_button(
            label="🚀 Download Schedule as PNG",
            data=buf,
            file_name="my_focus_schedule.png",
            mime="image/png",
            use_container_width=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin: 20px 0;'>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🗑️ Reset Schedule", use_container_width=True, type="secondary"):
        st.session_state.tasks = {day: [] for day in days}
        st.session_state.focus_hours = {day: 0 for day in days}
        st.session_state.selected_day = days[0]
        st.session_state.editing_day = None
        st.session_state.editing_index = None
        st.session_state.clear_form = True
        if "form_key" not in st.session_state:
            st.session_state.form_key = 0
        st.session_state.form_key += 1
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)