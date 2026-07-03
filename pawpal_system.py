"""PawPal+ core domain model.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
methods raise NotImplementedError until they are filled in incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Owner:
    """The pet owner and their daily time constraints/preferences."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    day_end: time = time(21, 0)
    preferences: dict = field(default_factory=dict)

    def total_available_time(self) -> int:
        """Minutes available for care within the owner's day window."""
        raise NotImplementedError

    def add_preference(self, key: str, value) -> None:
        """Record an owner preference (e.g. 'no meds after 8pm')."""
        raise NotImplementedError


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, grooming, etc.)."""

    name: str
    duration: int
    priority: str
    category: str = "general"
    recurrence: str = "daily"
    scheduled_time: time | None = None

    def priority_rank(self) -> int:
        """Numeric rank used for sorting (lower = more important)."""
        raise NotImplementedError

    def is_due_today(self, today: date) -> bool:
        """Whether this task should run on the given date (handles recurrence)."""
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


@dataclass
class Pet:
    """The pet being cared for, along with its list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's current tasks."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily care plan for a pet within the owner's constraints."""

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.plan: list[Task] = []
        self.skipped: list[Task] = []

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority, then duration."""
        raise NotImplementedError

    def generate_plan(self) -> list[Task]:
        """Assign start times and fit tasks within the available time budget."""
        raise NotImplementedError

    def resolve_conflicts(self) -> None:
        """Adjust or drop tasks whose time slots overlap."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return human-readable reasoning for the generated plan."""
        raise NotImplementedError

    def total_planned_time(self) -> int:
        """Total minutes consumed by the scheduled tasks."""
        raise NotImplementedError
