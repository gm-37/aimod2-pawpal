"""PawPal+ core domain model.

One Owner has many Pets; each Pet owns its care Tasks. The Scheduler plans
across all of the owner's pets within a shared daily time budget.

Convention: only Scheduler.generate_plan() mutates state (self.plan,
self.skipped, and each task's scheduled_time). Every other method is pure —
it reads its inputs and returns a value without side effects.

Mechanical helpers are implemented; the real scheduling logic is stubbed
(raises NotImplementedError) and filled in incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta

# Days until the next occurrence, keyed by recurrence.
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}

# Glyph shown at the start of a rendered task line, keyed by completion_status.
STATUS_MARKERS = {"pending": "○", "completed": "✓", "skipped": "✗"}

# Lower rank = more important. Used for sorting; avoids a separate enum class.
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


def time_to_minutes(t: time) -> int:
    """Minutes since midnight for a time-of-day."""
    return t.hour * 60 + t.minute


def minutes_to_time(total_minutes: int) -> time:
    """Convert minutes-since-midnight back to a time-of-day (wraps at 24h)."""
    total_minutes %= 24 * 60
    return time(total_minutes // 60, total_minutes % 60)


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, grooming, etc.)."""

    name: str
    duration: int  # minutes
    priority: str = "medium"  # "high" | "medium" | "low"
    category: str = "general"
    recurrence: str = "daily"  # "daily" | "weekly" | "none"
    due_date: date | None = None  # the day this occurrence is due; None = due whenever recurrence says
    scheduled_time: time | None = None  # set by Scheduler.generate_plan()
    fixed: bool = False  # True = scheduled_time is a pinned appointment; the scheduler honors it as-is
    # Back-reference to the owning pet; set in Pet.add_task. repr/compare off
    # to avoid recursive repr with Pet.tasks.
    pet: "Pet | None" = field(default=None, repr=False, compare=False)
    completion_status: str = "pending"  # "pending" | "completed" | "skipped"   

    def priority_rank(self) -> int:
        """Numeric rank for sorting (lower = more important; unknown sorts last)."""
        return PRIORITY_ORDER.get(self.priority.lower(), 99)

    def is_due_today(self, today: date) -> bool:
        """Whether this task should run on the given date (handles recurrence).

        When an explicit due_date is set (e.g. on an auto-spawned next
        occurrence), the task is due once we've reached that day — this keeps
        a freshly-spawned successor from surfacing before its date. Without a
        due_date, fall back to the recurrence rule.
        """
        if self.due_date is not None:
            return today >= self.due_date
        recurrence = self.recurrence.lower()
        if recurrence == "daily":
            return True
        if recurrence == "weekly":
            # Without a specific anchor date, assume weekly tasks recur on Mondays.
            return today.weekday() == 0
        return False

    def format_line(self) -> str:
        """Render one plan line, e.g. '✓ 08:00 - Biscuit: Morning walk (30 min) [high]'.

        A leading glyph shows completion_status (○ pending, ✓ completed,
        ✗ skipped) so the same line reflects both the plan and its progress.
        """
        marker = STATUS_MARKERS.get(self.completion_status.lower(), "○")
        time_label = self.scheduled_time.strftime("%H:%M") if self.scheduled_time else "unscheduled"
        pet_name = self.pet.name if self.pet else "Unknown"
        return f"{marker} {time_label} - {pet_name}: {self.name} ({self.duration} min) [{self.priority}]"
    
    def mark_completed(self, today: date | None = None) -> "Task | None":
        """Mark the task as completed.

        If this is a recurring task ("daily" or "weekly"), a fresh pending
        instance is automatically created for the next occurrence and added
        to the same pet. Returns that new task, or None if nothing was
        spawned (non-recurring task, or no owning pet).

        `today` is the completion date used to compute the successor's
        due_date; it defaults to date.today().
        """
        self.completion_status = "completed"
        return self._spawn_next_occurrence(today or date.today())

    def _spawn_next_occurrence(self, today: date) -> "Task | None":
        """Create the next occurrence of a recurring task on the same pet.

        The clone copies every field but resets the per-occurrence state
        (scheduled_time -> None, completion_status -> "pending") and stamps
        the next due_date: daily -> +1 day, weekly -> +7 days. The next date
        is measured from this occurrence's own due_date when it has one, so a
        chain of completions stays anchored to the schedule rather than
        drifting; otherwise it's measured from `today`. One-off tasks
        ("none") and orphan tasks (no pet) spawn nothing.
        """
        interval = RECURRENCE_DAYS.get(self.recurrence.lower())
        if interval is None:
            return None
        if self.pet is None:
            return None
        base = self.due_date if self.due_date is not None else today
        next_due = base + timedelta(days=interval)
        # pet=None here; add_task sets the back-reference on the new instance.
        next_task = replace(
            self,
            due_date=next_due,
            scheduled_time=None,
            completion_status="pending",
            pet=None,
        )
        self.pet.add_task(next_task)
        return next_task

    def mark_skipped(self) -> None:
        """Mark the task as skipped."""
        self.completion_status = "skipped"


@dataclass
class Pet:
    """A pet being cared for, along with its list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure tasks passed at construction also get the back-reference.
        for task in self.tasks:
            task.pet = self

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)
        task.pet = None

    def list_tasks(self) -> list[Task]:
        """Return this pet's current tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """The pet owner, their pets, and their daily time constraints/preferences."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    day_end: time = time(21, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def total_available_time(self) -> int:
        """Minutes available for care, capped by the day_start..day_end window."""
        window = time_to_minutes(self.day_end) - time_to_minutes(self.day_start)
        return min(self.available_minutes, window)

    def add_preference(self, key: str, value) -> None:
        """Record an owner preference (e.g. 'no meds after 8pm'). Key is a string description; 
        value can be any type, describing any additional details."""
        self.preferences[key] = value


class Scheduler:
    """Builds a daily care plan across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped: list[Task] = []
        self.plan_date: date | None = None

    def collect_tasks(self) -> list[Task]:
        """Every task across every pet the owner has (each knows its pet)."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def sort_tasks(self, today: date) -> list[Task]:
        """Pure: today's due tasks ordered by priority, then duration."""
        tasks_due = [task for task in self.collect_tasks() if task.is_due_today(today)]
        return sorted(
            tasks_due,
            key=lambda task: (task.priority_rank(), task.duration, task.name.lower()),
        )

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Pure: tasks ordered chronologically by scheduled_time.

        Uses a lambda key that renders each time as a zero-padded "HH:MM"
        string — fixed-width HH:MM sorts lexicographically the same way it
        sorts chronologically, so plain string comparison is correct.
        Unscheduled tasks (scheduled_time is None) sort to the end via the
        sentinel "99:99".

        Defaults to the current plan when no list is passed.
        """
        if tasks is None:
            tasks = self.plan
        return sorted(
            tasks,
            key=lambda task: task.scheduled_time.strftime("%H:%M")
            if task.scheduled_time
            else "99:99",
        )

    def filter_tasks(
        self,
        tasks: list[Task] | None = None,
        *,
        completion_status: str | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Pure: tasks matching the given completion_status and/or pet_name.

        Both filters are optional and combine with AND — pass one, both, or
        neither. Matching is case-insensitive. Defaults to every task across
        the owner's pets when no list is passed.
        """
        if tasks is None:
            tasks = self.collect_tasks()

        result = tasks
        if completion_status is not None:
            wanted = completion_status.lower()
            result = [t for t in result if t.completion_status.lower() == wanted]
        if pet_name is not None:
            wanted = pet_name.lower()
            result = [t for t in result if t.pet is not None and t.pet.name.lower() == wanted]
        return result

    def generate_plan(self, today: date) -> list[Task]:
        """The one mutator: fit tasks into the budget, resolving overlaps as we go.

        Sets self.plan and self.skipped and assigns each planned task's
        scheduled_time. Returns self.plan.

        Fixed tasks (task.fixed and scheduled_time set) keep their pinned
        time as-is; every other task is (re)packed back-to-back from
        day_start into the remaining budget. Both kinds draw from the same
        time budget. Overlaps between a fixed slot and a packed task are not
        resolved here — call conflict_warning() to surface them.
        """
        all_tasks = self.collect_tasks()
        # Clear only auto-scheduled tasks; a fixed task keeps its pinned time
        # so re-running stays stable and pinned appointments are preserved.
        for task in all_tasks:
            if not task.fixed:
                task.scheduled_time = None

        available_minutes = self.owner.total_available_time()
        current_minutes = time_to_minutes(self.owner.day_start)
        end_minutes = time_to_minutes(self.owner.day_end)
        budget = min(available_minutes, end_minutes - current_minutes)

        self.plan = []
        self.skipped = []
        self.plan_date = today

        for task in self.sort_tasks(today):
            if task.fixed and task.scheduled_time is not None:
                # Honor the pinned time; still charge it against the budget.
                if task.duration <= budget:
                    self.plan.append(task)
                    budget -= task.duration
                else:
                    self.skipped.append(task)
            elif task.duration <= budget:
                task.scheduled_time = minutes_to_time(current_minutes)
                self.plan.append(task)
                current_minutes += task.duration
                budget -= task.duration
            else:
                self.skipped.append(task)

        # Present the plan chronologically, since fixed slots may fall
        # anywhere relative to the packed tasks.
        self.plan = self.sort_by_time(self.plan)
        return self.plan

    def find_conflicts(
        self, tasks: list[Task] | None = None
    ) -> list[tuple[Task, Task]]:
        """Pure: pairs of scheduled tasks whose time slots overlap.

        Two tasks conflict when their [start, start + duration) minute
        intervals overlap — this covers identical start times and partial
        overlaps alike, across the same pet or different pets. Back-to-back
        tasks (one ends exactly as the next begins) do NOT conflict, matching
        how generate_plan packs them. Tasks without a scheduled_time are
        ignored. Defaults to the current plan.
        """
        if tasks is None:
            tasks = self.plan

        scheduled = [t for t in tasks if t.scheduled_time is not None]
        # Sort by start so each task only needs to look ahead until a task
        # starts at/after its end — everything past that cannot overlap.
        scheduled.sort(key=lambda t: time_to_minutes(t.scheduled_time))

        conflicts: list[tuple[Task, Task]] = []
        for i, task_a in enumerate(scheduled):
            start_a = time_to_minutes(task_a.scheduled_time)
            end_a = start_a + task_a.duration
            for task_b in scheduled[i + 1 :]:
                start_b = time_to_minutes(task_b.scheduled_time)
                if start_b >= end_a:
                    break  # later tasks start even later; none can overlap
                conflicts.append((task_a, task_b))
        return conflicts

    def conflict_warning(self, tasks: list[Task] | None = None) -> str:
        """Pure: human-readable warning for any scheduling conflicts.

        Returns an empty string when there are none, so callers can treat it
        as falsy. This never raises on overlapping tasks — it reports them.
        """
        conflicts = self.find_conflicts(tasks)
        if not conflicts:
            return ""

        def slot(task: Task) -> str:
            pet_name = task.pet.name if task.pet else "Unknown"
            start = task.scheduled_time.strftime("%H:%M")
            end = minutes_to_time(
                time_to_minutes(task.scheduled_time) + task.duration
            ).strftime("%H:%M")
            return f"{pet_name}: {task.name} ({start}–{end})"

        lines = [f"⚠ {len(conflicts)} scheduling conflict(s) detected:"]
        for task_a, task_b in conflicts:
            lines.append(f"  - {slot(task_a)} overlaps {slot(task_b)}")
        return "\n".join(lines)

    def explain(self) -> str:
        """Pure: human-readable reasoning for the current plan."""
        if not self.plan and not self.skipped:
            return "No plan has been generated yet."

        lines = []
        total_minutes = self.total_planned_time()
        if self.plan:
            lines.append(
                f"Planned {len(self.plan)} task(s) totaling {total_minutes} minute(s):"
            )
            for task in self.plan:
                lines.append(f"  - {task.format_line()}")
        else:
            lines.append("No tasks were scheduled.")

        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} task(s) due to time constraints:")
            for task in self.skipped:
                pet_name = task.pet.name if task.pet else "Unknown"
                lines.append(
                    f"  - {pet_name}: {task.name} ({task.duration} min) [{task.priority}]"
                )

        return "\n".join(lines)

    def total_planned_time(self) -> int:
        """Pure: total minutes consumed by the scheduled tasks."""
        return sum(task.duration for task in self.plan)

    def __str__(self) -> str:
        """Readable daily plan, so print(scheduler) always looks clean."""
        header = f"Daily plan for {self.owner.name}"
        if self.plan_date is not None:
            header += f" — {self.plan_date:%A, %b %d}"

        lines = [header, "=" * 44]
        if self.plan:
            for task in self.plan:
                lines.append(f"  {task.format_line()}")
        else:
            lines.append("  (nothing scheduled)")

        if self.skipped:
            lines.append("")
            lines.append("  Skipped (ran out of time):")
            for task in self.skipped:
                lines.append(f"    - {task.name} ({task.duration} min)")

        warning = self.conflict_warning()
        if warning:
            lines.append("")
            for warning_line in warning.splitlines():
                lines.append(f"  {warning_line}")

        lines.append("-" * 44)
        lines.append(
            f"  Total planned: {self.total_planned_time()} min "
            f"of {self.owner.total_available_time()} min available"
        )
        return "\n".join(lines)
