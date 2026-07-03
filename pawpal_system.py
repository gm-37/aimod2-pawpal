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

from dataclasses import dataclass, field
from datetime import date, time

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
    scheduled_time: time | None = None  # set by Scheduler.generate_plan()
    # Back-reference to the owning pet; set in Pet.add_task. repr/compare off
    # to avoid recursive repr with Pet.tasks.
    pet: "Pet | None" = field(default=None, repr=False, compare=False)

    def priority_rank(self) -> int:
        """Numeric rank for sorting (lower = more important; unknown sorts last)."""
        return PRIORITY_ORDER.get(self.priority.lower(), 99)

    def is_due_today(self, today: date) -> bool:
        """Whether this task should run on the given date (handles recurrence)."""
        raise NotImplementedError

    def format_line(self) -> str:
        """Render one plan line, e.g. '08:00 - Biscuit: Morning walk (30 min) [high]'."""
        raise NotImplementedError


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
        """Record an owner preference (e.g. 'no meds after 8pm')."""
        self.preferences[key] = value


class Scheduler:
    """Builds a daily care plan across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped: list[Task] = []

    def collect_tasks(self) -> list[Task]:
        """Every task across every pet the owner has (each knows its pet)."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def sort_tasks(self, today: date) -> list[Task]:
        """Pure: today's due tasks ordered by priority, then duration."""
        raise NotImplementedError

    def generate_plan(self, today: date) -> list[Task]:
        """The one mutator: fit tasks into the budget, resolving overlaps as we go.

        Sets self.plan and self.skipped and assigns each planned task's
        scheduled_time. Returns self.plan.
        """
        raise NotImplementedError

    def explain(self) -> str:
        """Pure: human-readable reasoning for the current plan."""
        raise NotImplementedError

    def total_planned_time(self) -> int:
        """Pure: total minutes consumed by the scheduled tasks."""
        return sum(task.duration for task in self.plan)
