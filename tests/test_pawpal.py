from diagrams.pawpal_system import Pet, Task


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
