from datetime import date

from pawpal_system import Owner, Task, Pet, Scheduler

date = date.today()

owner = Owner(name="Alice", available_minutes=120)
pet1 = Pet(name="Buddy", species="Dog")
pet2 = Pet(name="Whiskers", species="Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)


task1 = Task(name="Feed Buddy", duration=15)
task2 = Task(name="Walk Buddy", duration=30)
task3 = Task(name="Feed Whiskers", duration=10)
pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

schedule = Scheduler(owner=owner)
schedule.generate_plan(date)
print(schedule)