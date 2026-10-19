"""Core classes for PawPal+, based on diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    pet_name: str = ""
    completed: bool = False

    def set_priority(self, priority: str) -> None:
        """Change this task's priority level."""
        self.priority = priority

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    preferences: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, stamping it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


class Owner:
    def __init__(self, name: str):
        """Create an owner with no pets yet."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets, combined."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """Reads tasks across all of an owner's pets and builds a daily plan."""

    def __init__(self):
        """Create a scheduler with an empty queue and no constraints."""
        self.task_queue: list[Task] = []
        self.constraints: dict = {}

    def build_schedule(self, owner: Owner, constraints: dict | None = None) -> list[Task]:
        """Build and store a priority-ordered plan from the owner's pending tasks."""
        self.constraints = constraints or {}
        available_minutes = self.constraints.get("available_minutes")

        pending_tasks = [task for task in owner.get_all_tasks() if not task.completed]
        ordered_tasks = sorted(
            pending_tasks, key=lambda task: PRIORITY_RANK.get(task.priority, 1)
        )

        if available_minutes is None:
            self.task_queue = ordered_tasks
            return self.task_queue

        scheduled: list[Task] = []
        minutes_used = 0
        for task in ordered_tasks:
            if minutes_used + task.duration_minutes > available_minutes:
                continue
            scheduled.append(task)
            minutes_used += task.duration_minutes

        self.task_queue = scheduled
        return self.task_queue

    def explain_plan(self) -> str:
        """Describe the most recently built plan as a readable string."""
        if not self.task_queue:
            return "No tasks scheduled."

        lines = ["Today's plan:"]
        for i, task in enumerate(self.task_queue, start=1):
            pet_label = f" for {task.pet_name}" if task.pet_name else ""
            lines.append(
                f"{i}. {task.description}{pet_label} "
                f"({task.duration_minutes} min, priority: {task.priority})"
            )
        return "\n".join(lines)
