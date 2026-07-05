import streamlit as st
from datetime import date, time

from pawpal_system import Owner, Task, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Persist domain objects in the session "vault" so they survive reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=120)
if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(st.session_state.pet)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

# Connect the input fields to our objects so edits flow into the logic.
st.session_state.owner.name = owner_name
st.session_state.pet.name = pet_name
st.session_state.pet.species = species

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Optionally pin a task to a fixed time; otherwise the scheduler places it.
pin_time = st.checkbox("Pin to a fixed time")
fixed_time = st.time_input("Fixed time", value=time(9, 0)) if pin_time else None

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
            "fixed_time": fixed_time.strftime("%H:%M") if pin_time else "—",
        }
    )
    st.session_state.pet.add_task(
        Task(
            name=task_title,
            duration=int(duration),
            priority=priority,
            scheduled_time=fixed_time if pin_time else None,
            fixed=pin_time,
        )
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.session_state.scheduler.generate_plan(date.today())
    st.text(str(st.session_state.scheduler))  # readable plan via Scheduler.__str__

    # Warn (don't crash) if any scheduled tasks overlap in time.
    warning = st.session_state.scheduler.conflict_warning()
    if warning:
        st.warning(warning)
