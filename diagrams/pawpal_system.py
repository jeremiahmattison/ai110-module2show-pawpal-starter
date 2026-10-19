"""Class skeletons for PawPal+, based on diagrams/uml.mmd.

No scheduling logic is implemented yet — just names, attributes, and method stubs.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    completed: bool = False

    def set_priority(self, priority: str) -> None:
        pass

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    preferences: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass


class Scheduler:
    def __init__(self):
        self.task_queue: list[Task] = []
        self.constraints: dict = {}

    def build_schedule(self, tasks: list[Task], constraints: dict) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass
