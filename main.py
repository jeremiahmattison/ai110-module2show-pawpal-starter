"""Demo script: build an Owner, two Pets, and a few Tasks, then print today's schedule."""

from diagrams.pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan")

    dog = Pet("Mochi", "dog", preferences=["morning walks"])
    cat = Pet("Luna", "cat", preferences=["quiet playtime"])
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks are added out of chronological order on purpose, to exercise sort_by_time().
    dog.add_task(Task("Feeding", duration_minutes=10, priority="high", time="18:00", frequency="daily"))
    dog.add_task(Task("Morning walk", duration_minutes=30, priority="high", time="07:00"))
    cat.add_task(Task("Playtime", duration_minutes=20, priority="low", time="16:30"))
    cat.add_task(Task("Litter box cleaning", duration_minutes=5, priority="medium", time="09:00"))

    # These two create conflicts on purpose, to exercise find_conflicts():
    dog.add_task(Task("Brushing", duration_minutes=10, priority="low", time="07:00"))  # same pet, same time as "Morning walk"
    cat.add_task(Task("Vet checkup", duration_minutes=30, priority="high", time="07:00"))  # different pet, same time

    scheduler = Scheduler()
    scheduler.build_schedule(owner, constraints={"available_minutes": 60})

    print("Today's Schedule (by priority)")
    print("===============================")
    print(scheduler.explain_plan())
    if scheduler.conflict_warning:
        print(f"\nWARNING: {scheduler.conflict_warning}")

    scheduler.sort_by_time()
    print("\nToday's Schedule (sorted by time)")
    print("===================================")
    print(scheduler.explain_plan())

    feeding = dog.get_tasks()[0]
    dog.mark_task_complete(feeding)  # "Feeding" is daily, so a fresh occurrence is scheduled

    print("\nMochi's tasks after completing the daily Feeding task")
    print("=======================================================")
    for task in dog.get_tasks():
        print(
            f"- [{task.due_date} {task.time}] {task.description} "
            f"(frequency: {task.frequency}, completed: {task.completed})"
        )

    print("\nIncomplete tasks")
    print("=================")
    for task in scheduler.filter_tasks(completed=False):
        print(f"- [{task.time}] {task.description} ({task.pet_name})")

    print("\nTasks for Mochi")
    print("================")
    for task in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"- [{task.time}] {task.description} (completed: {task.completed})")

    print("\nConflict check (re-run after completing a task)")
    print("================================================")
    scheduler.build_schedule(owner, constraints={"available_minutes": 60})
    print(scheduler.conflict_warning or "No scheduling conflicts.")


if __name__ == "__main__":
    main()
