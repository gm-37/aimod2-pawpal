from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_completed_changes_status():
    task = Task(name="Feed Buddy", duration=15)
    assert task.completion_status == "pending"

    task.mark_completed()

    assert task.completion_status == "completed"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Walk Buddy", duration=30))

    assert len(pet.tasks) == 1


# --- Helpers ---------------------------------------------------------------

TODAY = date(2026, 7, 5)  # a Sunday


def _owner_with_pet(available_minutes=120):
    """Owner + one pet, wired together. Returns (owner, pet)."""
    owner = Owner(name="Jordan", available_minutes=available_minutes)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    return owner, pet


# --- Behavior 1: generate_plan budget packing ------------------------------
# Happy path plus the edges: no tasks at all, and a task that can't fit.

def test_generate_plan_packs_tasks_back_to_back_in_priority_order():
    """Happy path: due tasks are packed from day_start (08:00) with no gaps,
    ordered by priority then duration, and returned chronologically."""
    owner, pet = _owner_with_pet(available_minutes=120)
    pet.add_task(Task(name="Walk", duration=30, priority="high"))
    pet.add_task(Task(name="Feed", duration=15, priority="high"))
    pet.add_task(Task(name="Groom", duration=20, priority="low"))
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan(TODAY)

    # Among "high" tasks, shorter duration wins: Feed (15) before Walk (30).
    # "low" Groom comes last. Packed from 08:00 with no gaps.
    assert [t.name for t in plan] == ["Feed", "Walk", "Groom"]
    assert [t.scheduled_time for t in plan] == [time(8, 0), time(8, 15), time(8, 45)]
    assert scheduler.skipped == []
    assert scheduler.total_planned_time() == 65


def test_generate_plan_with_no_tasks_is_empty_and_does_not_crash():
    """Edge: an owner whose pet has no tasks produces an empty plan."""
    owner, _pet = _owner_with_pet()
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan(TODAY)

    assert plan == []
    assert scheduler.skipped == []
    assert scheduler.total_planned_time() == 0


def test_generate_plan_skips_task_that_exceeds_remaining_budget():
    """Edge: budget boundary. The first task consumes the budget exactly;
    the second can't fit and is skipped rather than dropped silently."""
    owner, pet = _owner_with_pet(available_minutes=30)
    # "fits" is high priority so it's scheduled first and consumes the whole
    # 30-min budget exactly; "too_big" (lower priority) then has nothing left.
    fits = Task(name="Walk", duration=30, priority="high")
    too_big = Task(name="Groom", duration=15, priority="medium")
    pet.add_task(fits)
    pet.add_task(too_big)
    scheduler = Scheduler(owner)

    scheduler.generate_plan(TODAY)

    assert scheduler.plan == [fits]
    assert scheduler.skipped == [too_big]


# --- Behavior 2: sort_tasks ordering ---------------------------------------

def test_sort_tasks_orders_by_priority_then_duration_then_name():
    """Priority is primary; ties break by shorter duration, then name."""
    owner, pet = _owner_with_pet()
    low = Task(name="Groom", duration=10, priority="low")
    high_long = Task(name="Walk", duration=30, priority="high")
    high_short_z = Task(name="Zoomies", duration=15, priority="high")
    high_short_a = Task(name="Apple treat", duration=15, priority="high")
    for t in (low, high_long, high_short_z, high_short_a):
        pet.add_task(t)
    scheduler = Scheduler(owner)

    ordered = scheduler.sort_tasks(TODAY)

    # high first; within high, duration 15 before 30; the two 15s break by name.
    assert ordered == [high_short_a, high_short_z, high_long, low]


# --- Behavior 3: recurring task spawning -----------------------------------
# Happy path (daily), the weekly interval, and the non-recurring edge.

def test_completing_daily_task_spawns_next_occurrence_one_day_later():
    """Happy path: completing a daily task adds a fresh pending successor
    to the same pet, due the next day, with per-occurrence state reset."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(name="Walk", duration=30, recurrence="daily",
                due_date=TODAY, scheduled_time=time(8, 0))
    pet.add_task(task)

    successor = task.mark_completed(today=TODAY)

    assert task.completion_status == "completed"
    assert successor is not None
    assert successor in pet.tasks
    assert successor.due_date == date(2026, 7, 6)
    assert successor.completion_status == "pending"
    assert successor.scheduled_time is None
    assert len(pet.tasks) == 2


def test_completing_weekly_task_spawns_successor_seven_days_later():
    """Weekly recurrence advances the successor's due_date by 7 days."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(name="Bath", duration=45, recurrence="weekly", due_date=TODAY)
    pet.add_task(task)

    successor = task.mark_completed(today=TODAY)

    assert successor.due_date == date(2026, 7, 12)


def test_completing_non_recurring_task_spawns_nothing():
    """Edge: a one-off ('none') task completes without spawning a successor."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(name="Vet visit", duration=60, recurrence="none")
    pet.add_task(task)

    successor = task.mark_completed(today=TODAY)

    assert successor is None
    assert len(pet.tasks) == 1


# --- Behavior 3b: is_due_today recurrence filter ---------------------------
# The rules that decide whether a task surfaces on a given day. TODAY
# (2026-07-05) is a Sunday; MONDAY is the next day.

MONDAY = date(2026, 7, 6)


def test_daily_task_is_due_every_day():
    """A daily task with no due_date surfaces on any date."""
    task = Task(name="Walk", duration=30, recurrence="daily")
    assert task.is_due_today(TODAY) is True       # Sunday
    assert task.is_due_today(MONDAY) is True       # Monday
    assert task.is_due_today(date(2026, 7, 11)) is True  # Saturday


def test_weekly_task_is_due_only_on_monday():
    """Without a due_date, a weekly task recurs on Mondays only."""
    task = Task(name="Bath", duration=45, recurrence="weekly")
    assert task.is_due_today(TODAY) is False       # Sunday
    assert task.is_due_today(MONDAY) is True        # Monday


def test_non_recurring_task_without_due_date_is_never_due():
    """A 'none' task with no due_date never surfaces via the recurrence rule."""
    task = Task(name="Vet visit", duration=60, recurrence="none")
    assert task.is_due_today(TODAY) is False
    assert task.is_due_today(MONDAY) is False


def test_due_date_gates_a_task_until_its_day():
    """An explicit due_date overrides recurrence: not due before, due on/after."""
    task = Task(name="Nail trim", duration=15, recurrence="daily", due_date=MONDAY)
    assert task.is_due_today(TODAY) is False        # day before due_date
    assert task.is_due_today(MONDAY) is True         # exactly the due_date
    assert task.is_due_today(date(2026, 7, 7)) is True  # after due_date


def test_chained_completions_stay_anchored_and_do_not_drift():
    """Completing a spawned successor advances its due_date from the previous
    due_date (+interval), not from the completion day — so a chain of late
    completions stays on schedule instead of drifting forward."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(name="Walk", duration=30, recurrence="daily", due_date=TODAY)
    pet.add_task(task)

    first = task.mark_completed(today=TODAY)
    assert first.due_date == MONDAY

    # Complete the successor "late" (two days after it was due); its own
    # successor is still anchored to due_date + 1, not today + 1.
    second = first.mark_completed(today=date(2026, 7, 8))
    assert second.due_date == date(2026, 7, 7)


# --- Behavior 4: conflict detection ----------------------------------------
# The classic pair: exact-same-time overlaps, back-to-back does not.

def test_two_tasks_at_the_exact_same_time_conflict():
    """Edge: two tasks pinned to the identical start time overlap."""
    owner, pet = _owner_with_pet()
    a = Task(name="Walk", duration=30, scheduled_time=time(8, 0))
    b = Task(name="Feed", duration=15, scheduled_time=time(8, 0))
    pet.add_task(a)
    pet.add_task(b)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts([a, b])

    assert len(conflicts) == 1
    assert a in conflicts[0] and b in conflicts[0]
    assert scheduler.conflict_warning([a, b]) != ""


def test_back_to_back_tasks_do_not_conflict():
    """Happy path: one task ending exactly as the next begins is fine."""
    owner, pet = _owner_with_pet()
    a = Task(name="Walk", duration=30, scheduled_time=time(8, 0))   # 08:00–08:30
    b = Task(name="Feed", duration=15, scheduled_time=time(8, 30))  # 08:30–08:45
    pet.add_task(a)
    pet.add_task(b)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts([a, b]) == []
    assert scheduler.conflict_warning([a, b]) == ""
