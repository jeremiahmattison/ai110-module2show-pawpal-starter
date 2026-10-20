# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design centered on three core user actions: adding a pet, setting task priorities, and viewing the day's tasks. The UML draft included the following classes:

- **Pet** — stores basic info about an animal (name, species, preferences) and holds the list of care tasks associated with it. Supports adding a new pet to the system.
- **Task** — represents a single pet care task, including its title, duration, and priority level (low/medium/high). Priorities are set when a task is created or edited.
- **Owner** — represents the pet owner and their collection of pets.
- **Scheduler/Planner** — takes the pets' tasks and constraints (time, priority, preferences) and builds the day's schedule, so the user can see daily tasks in order along with the reasoning behind that order.

Each class has a focused responsibility: `Pet` and `Owner` manage identity and ownership data, `Task` captures what needs to be done and how urgently, and the `Scheduler` is solely responsible for turning a set of tasks into an ordered daily plan.

**b. Design changes**

Yes. While reviewing the UML against the class skeleton, I found two gaps and fixed both:

- **Added `pet_name` to `Task`.** The original design had `Pet` hold a list of `Task`s but gave `Task` no way to reference its owner back. Once `Scheduler.build_schedule()` flattens tasks from multiple pets into a single list, that link would be lost — the daily plan output wouldn't know which pet each task belonged to. Adding `pet_name` to `Task` keeps that information attached to the task itself.
- **Clarified the `Scheduler` ↔ `Pet` relationship.** The UML originally showed `Scheduler ..> Pet : reads`, but `build_schedule()` only ever takes a `List~Task~`, not `Pet` objects — the diagram didn't match the intended code. I removed that relationship and added `Owner ..> Scheduler : uses` instead, since it's the `Owner` that gathers tasks across its pets and asks the `Scheduler` to build a plan.
- **Noted the `build_schedule()` / `explain_plan()` coupling.** `explain_plan()` takes no arguments, so it has to describe whatever `build_schedule()` most recently produced. I added comments to the stubs making explicit that `build_schedule()` is expected to store its result in `self.task_queue` so `explain_plan()` has something to describe.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`Scheduler.find_conflicts()` only flags two tasks as conflicting when their `due_date` and `time` strings match *exactly* — it does not check whether their durations actually overlap. A 30-minute "Morning walk" at 07:00 and a 10-minute "Brushing" also at 07:00 get flagged (correct), but a 30-minute "Morning walk" at 07:00 and a 10-minute "Feeding" starting at 07:15 would not be flagged, even though the walk is still running when the feeding is supposed to start.

I chose this on purpose: comparing exact `(due_date, time)` keys lets conflict detection stay a single O(n) pass with a dict (`groups.setdefault((due_date, time), []).append(task)`), while true overlap detection would mean parsing every `"HH:MM"` string into minutes, computing each task's `[start, start + duration)` interval, and comparing every pair within a day — a harder, more error-prone piece of logic for a feature that's meant to be a lightweight, non-blocking warning rather than a real calendar engine. For PawPal+'s actual use case — a pet owner skimming a short daily task list — catching the common case of "I told it to do two things at once" is more valuable than perfect overlap math, and the cost of the gap is low: a missed near-overlap just means the owner sees one less warning, not a broken schedule.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code across the whole pipeline: turning brainstormed class descriptions into the `uml.mmd` diagram, generating the Python class skeleton (`pawpal_system.py`), fleshing that skeleton into real scheduling logic, writing `main.py` as a runnable demo, writing the unit tests, and drafting README sections. The most useful prompt was asking it to review the design for "missing relationships or potential logic bottlenecks" before I moved from skeleton to real implementation — that single question surfaced a real mismatch between the diagram and the planned code (the UML showed `Scheduler` reading from `Pet` directly, but the method was only ever going to take a flat list of `Task`s, which would have silently lost the pet-to-task mapping once a schedule spanned multiple pets).

**b. Judgment and verification**

I did not just accept the AI's claim that code "works" — I ran it myself after every change. Two concrete catches:

- The first version of `Scheduler.build_schedule()` used the `dict | None` type-hint syntax. The AI's own smoke test used `python3` without checking which interpreter/version that was. When I ran it in this repo's actual environment (Python 3.9, per `python3 --version`), it crashed immediately with a `TypeError`, since that union syntax needs Python 3.10+. I had the AI add `from __future__ import annotations` and reran the script to confirm it worked before accepting the change.
- When the test file was added, running plain `pytest` failed to import `diagrams.pawpal_system` (only `python -m pytest` worked), because bare `pytest` doesn't add the project root to `sys.path` the same way. Rather than accept "the tests pass" at face value, I asked for both invocation styles to be checked, which led to adding `conftest.py` so the import resolves consistently either way.

In both cases, the fix itself came from the AI, but I didn't trust it until I'd re-run `main.py` and `pytest` myself and seen the actual output change.

**c. AI Strategy**

*Which features were most effective?*
The biggest help was Claude actually reading my files before suggesting anything instead of just guessing. When I asked for tests or UI changes, it opened up `pawpal_system.py` and `app.py` first and based its suggestions on the real method signatures (like `find_conflicts()` returning a list of groups, not just true/false). That kept me from getting generic code that didn't actually match what I'd built. Being able to run `pytest` or `python main.py` right there and see real output in the same conversation also made it a lot faster to catch mistakes than copy-pasting code back and forth somewhere else.

*An AI suggestion I rejected or modified:*
While wiring the Streamlit UI up to the Scheduler, the easy move would've been to just call `build_schedule()` automatically every time the page reruns so the schedule and conflict warnings are always "live." I didn't want that — the whole point of having "Generate schedule" and "Sort by time" buttons is that the user explicitly triggers those actions, and quietly rebuilding the schedule in the background would make the buttons pointless and could reorder tasks the user didn't ask to reorder. So I kept schedule-building explicit (only on button click) and only made the conflict check itself live, since checking for conflicts doesn't change any state — it just tells you something.

*How separate chat sessions helped:*
I split the work into different chats by phase — one for the UML/class skeleton stage, one for the actual scheduling logic, and this one just for testing and polish. I started this chat by telling it straight up that it would only be about testing, and that kept it from trying to redesign decisions I'd already made — it just worked with what already existed. It also made it way easier to go back later and find exactly where a decision got made instead of scrolling through one giant chat covering everything at once.

*Lead architect takeaway:*
The main thing I learned is that even when the AI can write working code fast, I still have to be the one deciding what the system should actually do and why. Claude is good at implementing something once I describe it, and good at catching stuff like a broken sort or a missing edge case, but it doesn't know which tradeoffs actually matter for my scenario (like whether conflict detection needs to check overlapping durations or just exact time matches) unless I tell it. My job ended up being less "write every line myself" and more "decide what's correct, catch what doesn't fit, and make it explain its reasoning when something looks off."

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
