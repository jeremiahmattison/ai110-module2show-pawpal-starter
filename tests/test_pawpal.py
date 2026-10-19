from datetime import date, timedelta

from diagrams.pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", duration_minutes=10, priority="high"))

    assert len(pet.get_tasks()) == 1


def test_sort_by_time_orders_tasks_chronologically():
    scheduler = Scheduler()
    scheduler.task_queue = [
        Task("Dinner", duration_minutes=15, time="18:30"),
        Task("Breakfast", duration_minutes=10, time="07:00"),
        Task("Walk", duration_minutes=20, time="12:15"),
    ]

    ordered = scheduler.sort_by_time()

    assert [task.description for task in ordered] == ["Breakfast", "Walk", "Dinner"]
    assert ordered == scheduler.task_queue


def test_mark_complete_on_daily_task_schedules_next_day():
    task = Task("Feeding", duration_minutes=10, priority="high", frequency="daily")

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == (date.today() + timedelta(days=1)).isoformat()


def test_mark_complete_on_once_task_returns_none():
    task = Task("Vet visit", duration_minutes=60, frequency="once")

    next_task = task.mark_complete()

    assert next_task is None


def test_pet_mark_task_complete_adds_next_occurrence_to_pet():
    pet = Pet("Mochi", "dog")
    task = Task("Feeding", duration_minutes=10, frequency="daily")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task)

    assert next_task is not None
    assert next_task in pet.get_tasks()
    assert len(pet.get_tasks()) == 2


def test_find_conflicts_flags_duplicate_times():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    today = date.today().isoformat()
    task_a = Task("Walk", duration_minutes=20, time="08:00", due_date=today)
    task_b = Task("Medication", duration_minutes=5, time="08:00", due_date=today)
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts(owner)

    assert len(conflicts) == 1
    assert {task.description for task in conflicts[0]} == {"Walk", "Medication"}


def test_find_conflicts_ignores_same_time_different_date():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    pet.add_task(Task("Walk", duration_minutes=20, time="08:00", due_date=today))
    pet.add_task(Task("Medication", duration_minutes=5, time="08:00", due_date=tomorrow))

    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts(owner)

    assert conflicts == []


def test_explain_conflicts_describes_duplicate_times():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    today = date.today().isoformat()
    pet.add_task(Task("Walk", duration_minutes=20, time="08:00", due_date=today))
    pet.add_task(Task("Medication", duration_minutes=5, time="08:00", due_date=today))

    scheduler = Scheduler()
    message = scheduler.explain_conflicts(owner)

    assert "Walk" in message
    assert "Medication" in message
    assert "08:00" in message
