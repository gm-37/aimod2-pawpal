import streamlit as st
from datetime import date, time

from pawpal_system import (
    Owner,
    Task,
    Pet,
    Scheduler,
    time_to_minutes,
    minutes_to_time,
)

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
st.caption("Generate a prioritized daily plan, then review conflicts and filter the results.")


def _slot_label(task: Task) -> tuple[str, str]:
    """Return a task's (start, end) as 'HH:MM' strings for display."""
    start = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "—"
    if task.scheduled_time is None:
        return start, "—"
    end = minutes_to_time(
        time_to_minutes(task.scheduled_time) + task.duration
    ).strftime("%H:%M")
    return start, end


def _plan_rows(tasks: list[Task]) -> list[dict]:
    """Build professional, human-readable table rows from a list of tasks."""
    rows = []
    for task in tasks:
        start, end = _slot_label(task)
        pet_name = task.pet.name if task.pet else "Unknown"
        rows.append(
            {
                "Time": f"{start}–{end}" if start != "—" else "unscheduled",
                "Pet": pet_name,
                "Task": task.name,
                "Duration": f"{task.duration} min",
                "Priority": task.priority.title(),
                "Status": task.completion_status.title(),
            }
        )
    return rows


if st.button("Generate schedule", type="primary"):
    st.session_state.scheduler.generate_plan(date.today())
    st.session_state.schedule_generated = True

if st.session_state.get("schedule_generated"):
    scheduler = st.session_state.scheduler

    # --- Conflicts first: they're the most actionable thing for an owner. ---
    conflicts = scheduler.find_conflicts()
    if conflicts:
        st.error(
            f"⚠️ {len(conflicts)} scheduling conflict(s) need your attention — "
            "these tasks are booked at overlapping times."
        )
        for task_a, task_b in conflicts:
            # Suggest moving the lower-priority task; it's the safer one to shift.
            keep, move = (
                (task_a, task_b)
                if task_a.priority_rank() <= task_b.priority_rank()
                else (task_b, task_a)
            )
            a_start, a_end = _slot_label(task_a)
            b_start, b_end = _slot_label(task_b)
            pet_a = task_a.pet.name if task_a.pet else "Unknown"
            pet_b = task_b.pet.name if task_b.pet else "Unknown"
            with st.container(border=True):
                st.markdown(
                    f"**{pet_a}: {task_a.name}** ({a_start}–{a_end}) "
                    f"overlaps **{pet_b}: {task_b.name}** ({b_start}–{b_end})"
                )
                st.caption(
                    f"💡 You can't be in two places at once. Consider pinning "
                    f"**{move.name}** to a different time, shortening one task, "
                    f"or letting **{keep.name}** ({keep.priority} priority) keep this slot."
                )
    else:
        st.success("✅ No scheduling conflicts — every task has its own time slot.")

    # --- The plan itself, with filters, presented as a clean table. ---
    if scheduler.plan:
        st.success(
            f"Planned {len(scheduler.plan)} task(s) · "
            f"{scheduler.total_planned_time()} of "
            f"{scheduler.owner.total_available_time()} min used"
        )

        col_pet, col_status = st.columns(2)
        with col_pet:
            pet_names = [p.name for p in scheduler.owner.pets]
            pet_choice = st.selectbox("Filter by pet", ["All pets", *pet_names])
        with col_status:
            status_choice = st.selectbox(
                "Filter by status", ["All", "pending", "completed", "skipped"]
            )

        # Let the Scheduler do the filtering, then present chronologically.
        filtered = scheduler.filter_tasks(
            scheduler.plan,
            completion_status=None if status_choice == "All" else status_choice,
            pet_name=None if pet_choice == "All pets" else pet_choice,
        )
        filtered = scheduler.sort_by_time(filtered)

        if filtered:
            st.table(_plan_rows(filtered))
        else:
            st.info("No planned tasks match the current filters.")
    else:
        st.info("No tasks could be scheduled within the available time.")

    # --- Skipped tasks: surfaced so nothing silently disappears. ---
    if scheduler.skipped:
        st.warning(
            f"⏰ {len(scheduler.skipped)} task(s) didn't fit in today's time budget:"
        )
        st.table(_plan_rows(scheduler.skipped))

    # Keep the plain-text plan available for reference / copy-paste.
    with st.expander("Full text plan"):
        st.text(str(scheduler))
