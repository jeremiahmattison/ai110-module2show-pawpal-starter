import streamlit as st

from diagrams.pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.divider()

st.subheader("Owner & Pets")
owner.name = st.text_input("Owner name", value=owner.name)

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))

if owner.get_pets():
    st.write("Current pets:", ", ".join(pet.name for pet in owner.get_pets()))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks to a pet. These feed into the scheduler.")

if not owner.get_pets():
    st.info("Add a pet before adding tasks.")
else:
    pet_names = [pet.name for pet in owner.get_pets()]
    selected_pet_name = st.selectbox("Which pet is this task for?", pet_names)
    selected_pet = next(pet for pet in owner.get_pets() if pet.name == selected_pet_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_description = st.text_input("Task description", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        task_time = st.time_input("Time")
    with col5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                task_description,
                duration_minutes=int(duration),
                priority=priority,
                time=task_time.strftime("%H:%M"),
                frequency=frequency,
            )
        )

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "pet": task.pet_name,
                    "due_date": task.due_date,
                    "time": task.time,
                    "description": task.description,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "frequency": task.frequency,
                    "completed": task.completed,
                }
                for task in all_tasks
            ]
        )

        incomplete_tasks = [task for task in all_tasks if not task.completed]
        if incomplete_tasks:
            task_labels = [
                f"{task.pet_name} - {task.description} ({task.due_date} {task.time})"
                for task in incomplete_tasks
            ]
            selected_label = st.selectbox("Mark a task complete", task_labels)
            selected_task = incomplete_tasks[task_labels.index(selected_label)]

            if st.button("Mark complete"):
                owning_pet = next(
                    pet for pet in owner.get_pets() if pet.name == selected_task.pet_name
                )
                next_task = owning_pet.mark_task_complete(selected_task)
                if next_task is not None:
                    st.success(
                        f"Completed! Next occurrence scheduled for {next_task.due_date} at {next_task.time}."
                    )
                else:
                    st.success("Completed!")

        live_conflicts = scheduler.find_conflicts(owner)
        if live_conflicts:
            st.warning(scheduler.explain_conflicts(owner))
        else:
            st.success("No scheduling conflicts.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan from every pet's tasks, ordered by priority.")

available_minutes = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=1440, value=60
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate schedule"):
        scheduler.build_schedule(owner, constraints={"available_minutes": int(available_minutes)})
        minutes_used = sum(task.duration_minutes for task in scheduler.task_queue)
        st.success(
            f"Schedule built: {len(scheduler.task_queue)} task(s), "
            f"{minutes_used}/{int(available_minutes)} minutes used."
        )
with col2:
    if st.button("Sort by time"):
        scheduler.sort_by_time()
        st.success("Tasks sorted chronologically.")

if scheduler.task_queue:
    st.text(scheduler.explain_plan())

    st.caption("Filter the schedule below (uses `Scheduler.filter_tasks`).")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Pet", ["All"] + [pet.name for pet in owner.get_pets()], key="pet_filter"
        )
    with col2:
        status_filter = st.selectbox("Status", ["All", "Completed", "Incomplete"], key="status_filter")

    completed_arg = {"Completed": True, "Incomplete": False}.get(status_filter)
    pet_name_arg = None if pet_filter == "All" else pet_filter
    filtered_tasks = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_name_arg)

    st.table(
        [
            {
                "pet": task.pet_name,
                "due_date": task.due_date,
                "time": task.time,
                "description": task.description,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "completed": task.completed,
            }
            for task in filtered_tasks
        ]
        if filtered_tasks
        else []
    )
    if not filtered_tasks:
        st.info("No tasks match this filter.")

if scheduler.task_queue:
    if scheduler.conflict_warning:
        st.warning(scheduler.conflict_warning)
    else:
        st.success("No scheduling conflicts in this plan.")
