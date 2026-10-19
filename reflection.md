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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
