# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation Summary

The core logic lives in [`diagrams/pawpal_system.py`](diagrams/pawpal_system.py) as four classes:

- **`Task`** — a single care activity (`description`, `duration_minutes`, `priority`, `frequency`, `completed`, and the `pet_name` it belongs to). Can mark itself complete or change priority.
- **`Pet`** — a pet's basic info (`name`, `species`, `preferences`) plus its own list of `Task`s. `add_task()` stamps each task with the pet's name so it can be traced back after tasks from multiple pets are combined.
- **`Owner`** — holds a list of `Pet`s and exposes `get_all_tasks()`, which flattens every pet's tasks into one list. This is the single entry point the scheduler uses to see tasks across all pets, instead of looking at one pet at a time.
- **`Scheduler`** — the "brain." `build_schedule(owner, constraints)` reads `owner.get_all_tasks()`, drops completed tasks, sorts the rest by priority, and (if an `available_minutes` constraint is given) keeps adding tasks until the time budget runs out. `explain_plan()` turns the stored result into a readable, numbered plan.

`main.py` ties it together as a runnable demo: it builds an `Owner` with two `Pet`s, adds tasks with different durations/priorities, calls `build_schedule()`, and prints the plan via `explain_plan()` (see Sample Output below). `tests/test_pawpal.py` covers the two most important unit behaviors — marking a task complete, and a pet's task count increasing after `add_task()`.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule
=================
Today's plan:
1. Morning walk for Mochi (30 min, priority: high)
2. Feeding for Mochi (10 min, priority: high)
3. Litter box cleaning for Luna (5 min, priority: medium)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts `task_queue` chronologically with `sorted(..., key=lambda task: task.time)`. Works directly on `"HH:MM"` strings since they're zero-padded, so no parsing into a `datetime` is needed. This is in addition to the priority sort `build_schedule()` already does (high → medium → low). |
| Filtering | `Scheduler.filter_tasks(completed=None, pet_name=None)` | Returns tasks from `task_queue` matching completion status and/or pet name. Both filters are optional and combine with AND when both are given. |
| Conflict handling | `Scheduler.find_conflicts(owner)`, `Scheduler.explain_conflicts(owner)` | Groups every pending task across *all* of the owner's pets by `(due_date, time)` in one O(n) pass and flags any group with 2+ tasks — catching both one pet double-booked and two different pets scheduled at once. Only exact `(due_date, time)` matches are flagged, not overlapping durations (a deliberate tradeoff — see `reflection.md` section 2b). `build_schedule()` runs this automatically via the internal `_check_for_conflicts()` and stores the result as a string on `scheduler.conflict_warning` (or `None`), so a conflict never crashes the program — it's just a warning the UI/CLI can choose to display. |
| Recurring tasks | `Task.mark_complete()`, `Pet.mark_task_complete()` | Completing a `"daily"` or `"weekly"` task returns a fresh, incomplete clone of itself due `timedelta(days=1)` or `timedelta(weeks=1)` from *today* (not from the old due date, so a late completion still reschedules sensibly). `Pet.mark_task_complete()` is the method to call for this — it delegates to `task.mark_complete()` and adds whatever next-occurrence task comes back onto that pet's own task list, since `Task` itself has no way to reach back into its pet's list. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
