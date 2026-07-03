# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

core actions: add a pet, schedule a walk, see today's tasks (from ex)
3 additional core actions: schedule grooming appointments, store medications list, enter schedule constraints (like work hours, etc)

I included 4 main classes: Owner, Pet, Task, and Scheduler.

The Owner class is essentially the user themself. It includes their name, a list of their pets, their available time, and their preferences when it comes to caring for their pet. The methods for this class include changing these attributes and they control setting the preferences on how they'd like the schedule to be created. They can also add or remove their pets, of course.

The Pet class is for the pets. It includes name and species/breed attributes. There are methods for adding and removing tasks in this class so tasks are linked to the pets, which will help for owners with several pets.

The Task class is for the tasks the owner would like to schedule to care for their pet. The attributes of this class includes name, duration, priority, category, recurrence, and scheduled time for when they are scheduled by the app. Methods include getters for the priority and a string representation of the task object.

The Scheduler class does the main work of the app. It includes references to the pet the schedule is for, the owner, and a plan (list of Tasks). The methods sort tasks by their priority, generate a schedule, and explain the reasoning as well as provide the time duration of the full schedule.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Claude brought up a good point in that the scheduler could not easily adjust if an owner had multiple pets, so I made changes (with its help) to account for that and make sure the scheduler takes into account all tasks planned for all pets at the same time (so they all can fit into the owner's available time)


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
