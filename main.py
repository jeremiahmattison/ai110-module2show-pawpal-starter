"""Demo script: build an Owner, two Pets, and a few Tasks, then print today's schedule."""

from diagrams.pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan")

    dog = Pet("Mochi", "dog", preferences=["morning walks"])
    cat = Pet("Luna", "cat", preferences=["quiet playtime"])
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Morning walk", duration_minutes=30, priority="high"))
    dog.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    cat.add_task(Task("Litter box cleaning", duration_minutes=5, priority="medium"))
    cat.add_task(Task("Playtime", duration_minutes=20, priority="low"))

    scheduler = Scheduler()
    scheduler.build_schedule(owner, constraints={"available_minutes": 60})

    print("Today's Schedule")
    print("=================")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
