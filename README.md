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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Daily plan for Alice — Friday, Jul 03
============================================
  08:00 - Whiskers: Feed Whiskers (10 min) [medium]
  08:10 - Buddy: Feed Buddy (15 min) [medium]
  08:25 - Buddy: Walk Buddy (30 min) [medium]
--------------------------------------------
  Total planned: 55 min of 120 min available


## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov

```

The test suite covers sorting correctness and recurrence logic of the scheduler behaviors as well as checks conflict detection and ensures adding tasks and removing tasks and pet logic occurs as it should. All 16 tests have passed.

Sample test output:

```

platform darwin -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/kirmak/Desktop/CodePath/AI110/aimod2-pawpal
plugins: anyio-4.14.0
collected 16 items                                                                                        

tests/test_pawpal.py ...........                                                                    [100%]

=========================================== 16 passed in 0.02s ============================================
```
Confidence level: 4 out of 5 stars


## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time(), Scheduler.sort_tasks() | e.g., by priority, duration |
| Filtering | Scheduler.filter_tasks() | e.g., skip tasks if time runs out |
| Conflict handling | Scheduler.find_conflicts(), Scheduler.conflict_warning() | e.g., overlapping time slots |
| Recurring tasks | Task.mark_completed  | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Follow along without watching a video:

1. **Enter owner + pet info.** Type an owner name and pet name, and pick a species. These feed straight into the `Owner` and `Pet` objects held in session state.
2. **Add care tasks.** For each task, set a title, duration (minutes), and priority (low / medium / high). Optionally check **Pin to a fixed time** to lock a task to a set time (e.g. a 9:00 vet appointment); otherwise the scheduler places it for you. Added tasks appear in the "Current tasks" table.
3. **Generate the schedule.** Click **Generate schedule**. The `Scheduler` keeps today's due tasks, sorts them by priority (then shortest duration), and packs them back-to-back from the start of the day into the available time budget. Pinned tasks keep their time.
4. **Review conflict warnings.** If any tasks overlap in time, the app flags each overlapping pair and suggests moving the lower-priority task. If everything has its own slot, you get a "No scheduling conflicts" confirmation.
5. **Read the plan and filter it.** The plan is shown chronologically as a table (time, pet, task, duration, priority, status). Use the **Filter by pet** and **Filter by status** dropdowns to narrow it down.
6. **Check skipped tasks.** Any task that didn't fit the day's time budget is listed under a "didn't fit" warning so nothing silently disappears. Open **Full text plan** for a plain-text summary you can copy.

**Example workflow**
add a pet-->schedule task-->view today's schedule

(View sample output above)

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
