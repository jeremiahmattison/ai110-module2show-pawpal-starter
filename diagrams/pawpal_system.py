"""Core classes for PawPal+, based on diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    pet_name: str = ""
    completed: bool = False
    time: str = "00:00"  # scheduled time in "HH:MM" (24-hour) format
    due_date: str = field(default_factory=lambda: date.today().isoformat())  # "YYYY-MM-DD"

    def set_priority(self, priority: str) -> None:
        """Change this task's priority level."""
        self.priority = priority

    def mark_complete(self) -> Task | None:
        """Mark this task as completed, and schedule its next occurrence if it recurs.

        For a "daily" or "weekly" task, computes the next due date as
        `date.today() + FREQUENCY_INTERVALS[frequency]` (a `timedelta` of 1 or 7
        days) and returns a cloned, incomplete `Task` with that new due date.
        Using `date.today()` rather than this task's own `due_date` means a late
        completion still reschedules relative to today, not a stale past date.

        Returns:
            A new incomplete `Task` for the next occurrence, or `None` for a
            one-time ("once") task.
        """
        self.completed = True
        interval = FREQUENCY_INTERVALS.get(self.frequency)
        if interval is not None:
            next_due_date = date.today() + interval
            return replace(self, completed=False, due_date=next_due_date.isoformat())
        return None


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

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark one of this pet's tasks complete.

        Delegates the completion/recurrence logic to `task.mark_complete()`;
        this method's job is just to re-attach whatever next-occurrence task
        comes back (since `Task` itself doesn't hold a reference to its pet's
        task list).

        Args:
            task: One of this pet's own `Task` instances to complete.

        Returns:
            The newly scheduled next-occurrence `Task` if `task` recurs
            (daily/weekly), otherwise `None`.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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
        self.conflict_warning: str | None = None

    def build_schedule(self, owner: Owner, constraints: dict | None = None) -> list[Task]:
        """Build and store a priority-ordered plan from the owner's pending tasks.

        Collects every incomplete task across the owner's pets, sorts it by
        `priority` (high before medium before low), then greedily keeps adding
        tasks in that order until the next one would exceed
        `constraints["available_minutes"]` (a task that doesn't fit is skipped,
        not swapped for a shorter one later in the list). If no
        `available_minutes` constraint is given, every pending task is kept.
        Also runs the lightweight conflict check and stores its result on
        `self.conflict_warning` — see `_check_for_conflicts`.

        Args:
            owner: The owner whose pets' tasks should be scheduled.
            constraints: Optional dict; only `"available_minutes"` (int) is
                currently used to cap the plan's total duration.

        Returns:
            The ordered list of tasks that made it into the plan (also stored
            as `self.task_queue`).
        """
        self.constraints = constraints or {}
        available_minutes = self.constraints.get("available_minutes")

        pending_tasks = [task for task in owner.get_all_tasks() if not task.completed]
        ordered_tasks = sorted(
            pending_tasks, key=lambda task: PRIORITY_RANK.get(task.priority, 1)
        )

        if available_minutes is None:
            self.task_queue = ordered_tasks
        else:
            scheduled: list[Task] = []
            minutes_used = 0
            for task in ordered_tasks:
                if minutes_used + task.duration_minutes > available_minutes:
                    continue
                scheduled.append(task)
                minutes_used += task.duration_minutes

            self.task_queue = scheduled

        self._check_for_conflicts(owner)
        return self.task_queue

    def _check_for_conflicts(self, owner: Owner) -> None:
        """Run the lightweight conflict check and store a warning instead of raising.

        Stores the result on `self.conflict_warning`: a human-readable string
        if conflicts were found, or `None` if there were none. Any unexpected
        error during the check is caught and turned into a warning string too,
        so a bad conflict check can never stop `build_schedule()` from
        returning a plan.
        """
        try:
            self.conflict_warning = (
                self.explain_conflicts(owner) if self.find_conflicts(owner) else None
            )
        except Exception as error:
            self.conflict_warning = f"Could not check for conflicts: {error}"

    def sort_by_time(self) -> list[Task]:
        """Reorder the current task queue chronologically by each task's "HH:MM" time.

        Uses `sorted()` with a lambda key (`key=lambda task: task.time`); since
        `time` is always a zero-padded 24-hour string, plain string comparison
        already puts them in chronological order, so no parsing into minutes
        or a `datetime` is needed.

        Returns:
            The re-sorted task list (also stored as `self.task_queue`).
        """
        self.task_queue = sorted(self.task_queue, key=lambda task: task.time)
        return self.task_queue

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return tasks from the current queue matching the given completion status and/or pet name.

        Each filter is applied only if its argument isn't `None`, and the two
        filters combine with AND (both must match when both are given).

        Args:
            completed: If given, only keep tasks whose `completed` flag equals this.
            pet_name: If given, only keep tasks whose `pet_name` equals this.

        Returns:
            The filtered list of tasks from `self.task_queue`.
        """
        tasks = self.task_queue
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet_name == pet_name]
        return tasks

    def find_conflicts(self, owner: Owner) -> list[list[Task]]:
        """Return groups of pending tasks that share the same due date and time.

        Checks across all of the owner's pets, so a conflict can involve one
        pet with two tasks or two different pets both scheduled at once. Groups
        every incomplete task into a dict keyed by `(due_date, time)` in a
        single O(n) pass, then keeps only the groups with more than one task.

        Note: this only catches an exact `(due_date, time)` match, not
        overlapping durations (e.g. a 30-minute 07:00 task and a 07:15 task
        aren't flagged even though they'd actually overlap) — a deliberate
        tradeoff for a simple, fast check. See reflection.md section 2b.

        Args:
            owner: The owner whose pets' tasks should be checked.

        Returns:
            A list of conflict groups; each group is a list of 2+ tasks that
            share the same due date and time. Empty if there are no conflicts.
        """
        groups: dict[tuple[str, str], list[Task]] = {}
        for task in owner.get_all_tasks():
            if task.completed:
                continue
            groups.setdefault((task.due_date, task.time), []).append(task)

        return [group for group in groups.values() if len(group) > 1]

    def explain_conflicts(self, owner: Owner) -> str:
        """Describe any scheduling conflicts across the owner's pets as a readable string."""
        conflicts = self.find_conflicts(owner)
        if not conflicts:
            return "No scheduling conflicts."

        lines = ["Scheduling conflicts:"]
        for group in conflicts:
            due_date, time = group[0].due_date, group[0].time
            task_labels = ", ".join(f"{task.description} ({task.pet_name})" for task in group)
            lines.append(f"- {due_date} {time}: {task_labels}")
        return "\n".join(lines)

    def explain_plan(self) -> str:
        """Describe the most recently built plan as a readable string."""
        if not self.task_queue:
            return "No tasks scheduled."

        lines = ["Today's plan:"]
        for i, task in enumerate(self.task_queue, start=1):
            pet_label = f" for {task.pet_name}" if task.pet_name else ""
            lines.append(
                f"{i}. [{task.due_date} {task.time}] {task.description}{pet_label} "
                f"({task.duration_minutes} min, priority: {task.priority})"
            )
        return "\n".join(lines)
