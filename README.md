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

## ✨ Features

- **Priority-based daily scheduling** — `Scheduler.build_schedule()` collects every pending task across all of an owner's pets, orders them high → medium → low priority, and greedily fills the plan up to a configurable time budget (`available_minutes`), skipping any task that would overflow it.
- **Chronological sorting** — `Scheduler.sort_by_time()` re-orders the built schedule by time of day (`"HH:MM"`), independent of the priority order used to build it, so you can view the same plan either by importance or by when it actually happens.
- **Conflict warnings** — `Scheduler.find_conflicts()` / `explain_conflicts()` detect tasks scheduled at the exact same date and time, across *all* pets (not just within one), and surface a readable warning automatically whenever a schedule is built, plus live in the Streamlit UI as tasks are added.
- **Daily/weekly recurrence** — `Task.mark_complete()` reschedules a `"daily"` or `"weekly"` task's next occurrence relative to today automatically, so marking a recurring task done keeps the routine going without manual re-entry; one-time (`"once"`) tasks simply complete with no follow-up.
- **Status/pet filtering** — `Scheduler.filter_tasks()` narrows the current schedule by completion status and/or pet name, powering the filter dropdowns in the Streamlit UI.

See [📐 Smarter Scheduling](#-smarter-scheduling) below for method-level details and known tradeoffs.

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

The suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) covers the scheduling behaviors that matter most:

- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order.
- **Recurrence logic** — completing a `"daily"` task schedules a new, incomplete task for the next day (and a `"once"` task returns no follow-up).
- **Conflict detection** — `find_conflicts()`/`explain_conflicts()` flag tasks that share the same `(due_date, time)`, including across different pets, and correctly ignore same-time tasks on different dates.

```bash
python -m pytest
```

Sample test output:

```
================================================================ test session starts =================================================================
platform darwin -- Python 3.12.7, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/macbookpro/Desktop/AI110/ai110-module2show-pawpal-starter
plugins: Faker-37.1.0, anyio-4.2.0
collected 9 items                                                                                                                                    

tests/test_pawpal.py .........                                                                                                                 [100%]

================================================================= 9 passed in 0.28s ==================================================================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

The core scheduling behaviors — chronological sorting, recurrence, and conflict detection — all pass and cover both the happy path and key negative cases (e.g., same time on different dates correctly does *not* flag a conflict). Confidence isn't a full 5/5 because some areas remain untested: `build_schedule()`'s time-budget logic (e.g., `available_minutes` of 0 or a task too large to fit), `filter_tasks()`, and the known limitation that `find_conflicts()` only catches exact `(due_date, time)` matches, not overlapping durations (see `reflection.md` section 2b).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts `task_queue` chronologically with `sorted(..., key=lambda task: task.time)`. Works directly on `"HH:MM"` strings since they're zero-padded, so no parsing into a `datetime` is needed. This is in addition to the priority sort `build_schedule()` already does (high → medium → low). |
| Filtering | `Scheduler.filter_tasks(completed=None, pet_name=None)` | Returns tasks from `task_queue` matching completion status and/or pet name. Both filters are optional and combine with AND when both are given. |
| Conflict handling | `Scheduler.find_conflicts(owner)`, `Scheduler.explain_conflicts(owner)` | Groups every pending task across *all* of the owner's pets by `(due_date, time)` in one O(n) pass and flags any group with 2+ tasks — catching both one pet double-booked and two different pets scheduled at once. Only exact `(due_date, time)` matches are flagged, not overlapping durations (a deliberate tradeoff — see `reflection.md` section 2b). `build_schedule()` runs this automatically via the internal `_check_for_conflicts()` and stores the result as a string on `scheduler.conflict_warning` (or `None`), so a conflict never crashes the program — it's just a warning the UI/CLI can choose to display. |
| Recurring tasks | `Task.mark_complete()`, `Pet.mark_task_complete()` | Completing a `"daily"` or `"weekly"` task returns a fresh, incomplete clone of itself due `timedelta(days=1)` or `timedelta(weeks=1)` from *today* (not from the old due date, so a late completion still reschedules sensibly). `Pet.mark_task_complete()` is the method to call for this — it delegates to `task.mark_complete()` and adds whatever next-occurrence task comes back onto that pet's own task list, since `Task` itself has no way to reach back into its pet's list. |

## 📸 Demo Walkthrough

### What the UI lets you do

The Streamlit app (`app.py`) is organized into three sections:

- **Owner & Pets** — set the owner's name and add one or more pets (name + species). Each pet's tasks are tracked separately but feed into the same scheduler.
- **Tasks** — for a selected pet, add a task with a description, duration, priority (`low`/`medium`/`high`), time of day, and frequency (`once`/`daily`/`weekly`). Added tasks appear in a live table, and a dropdown lets you mark any incomplete task as done. A conflict warning (or a "no conflicts" success message) appears automatically underneath the task list as soon as two tasks share the same date and time.
- **Build Schedule** — set an available-minutes budget and click "Generate schedule" to build a priority-ordered plan (with a success message summarizing how many tasks and minutes were used), or "Sort by time" to reorder the same plan chronologically. The resulting schedule can be filtered by pet and by completion status, and any conflicts in the built plan are flagged with a warning.

### Example workflow

1. Add a pet (e.g., "Mochi", species "dog").
2. Add a few tasks for Mochi at different times, priorities, and frequencies — e.g., a `high`-priority "Morning walk" at `07:00`, a `daily` "Feeding" at `18:00`, and a `low`-priority "Brushing" also at `07:00`.
3. Notice the conflict warning appear immediately, since "Morning walk" and "Brushing" share the same time.
4. Set an available-minutes budget and click "Generate schedule" to see the tasks ordered by priority (high first), capped at the budget.
5. Click "Sort by time" to see the same tasks re-ordered chronologically instead.
6. Mark the "Feeding" task complete — since it's `daily`, a new incomplete "Feeding" task is automatically scheduled for tomorrow.
7. Use the pet/status filters to view just Mochi's incomplete tasks.

### Key Scheduler behaviors demonstrated

- **Priority sorting** (`build_schedule()`): high-priority tasks are scheduled before medium/low, within the available time budget.
- **Chronological sorting** (`sort_by_time()`): the same plan re-ordered by time of day instead of priority.
- **Conflict detection** (`find_conflicts()` / `explain_conflicts()`): two tasks at the same date and time are flagged, even across different pets.
- **Recurrence** (`mark_complete()`): completing a `daily`/`weekly` task spawns its next occurrence; a `once` task does not.
- **Filtering** (`filter_tasks()`): narrowing the schedule down by pet and/or completion status.

### Sample CLI output

Running `python main.py` drives the same `Scheduler`/`Owner`/`Pet` classes outside the UI, exercising priority scheduling, time sorting, recurrence, filtering, and conflict detection in sequence:

```
Today's Schedule (by priority)
===============================
Today's plan:
1. [2026-10-19 18:00] Feeding for Mochi (10 min, priority: high)
2. [2026-10-19 07:00] Morning walk for Mochi (30 min, priority: high)
3. [2026-10-19 09:00] Litter box cleaning for Luna (5 min, priority: medium)
4. [2026-10-19 07:00] Brushing for Mochi (10 min, priority: low)

WARNING: Scheduling conflicts:
- 2026-10-19 07:00: Morning walk (Mochi), Brushing (Mochi), Vet checkup (Luna)

Today's Schedule (sorted by time)
===================================
Today's plan:
1. [2026-10-19 07:00] Morning walk for Mochi (30 min, priority: high)
2. [2026-10-19 07:00] Brushing for Mochi (10 min, priority: low)
3. [2026-10-19 09:00] Litter box cleaning for Luna (5 min, priority: medium)
4. [2026-10-19 18:00] Feeding for Mochi (10 min, priority: high)

Mochi's tasks after completing the daily Feeding task
=======================================================
- [2026-10-19 18:00] Feeding (frequency: daily, completed: True)
- [2026-10-19 07:00] Morning walk (frequency: once, completed: False)
- [2026-10-19 07:00] Brushing (frequency: once, completed: False)
- [2026-10-20 18:00] Feeding (frequency: daily, completed: False)

Incomplete tasks
=================
- [07:00] Morning walk (Mochi)
- [07:00] Brushing (Mochi)
- [09:00] Litter box cleaning (Luna)

Tasks for Mochi
================
- [07:00] Morning walk (completed: False)
- [07:00] Brushing (completed: False)
- [18:00] Feeding (completed: True)

Conflict check (re-run after completing a task)
================================================
Scheduling conflicts:
- 2026-10-19 07:00: Morning walk (Mochi), Brushing (Mochi), Vet checkup (Luna)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
