from datetime import date, time

from pawpal_system import Owner, Task, Pet, Scheduler

date = date.today()

owner = Owner(name="Alice", available_minutes=120)
pet1 = Pet(name="Buddy", species="Dog")
pet2 = Pet(name="Whiskers", species="Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)


task1 = Task(name="Feed Buddy", duration=15, scheduled_time=time(12,0), fixed=True)
task2 = Task(name="Walk Buddy", duration=30, scheduled_time=time(10,30), fixed=True)
task3 = Task(name="Feed Whiskers", duration=10, scheduled_time=time(12,0), fixed=True)
pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

schedule = Scheduler(owner=owner)
#print(schedule.sort_by_time(schedule.collect_tasks()))
#print(schedule.filter_tasks(pet_name="Buddy"))
#print(schedule.filter_tasks(completion_status="completed"))
schedule.generate_plan(date)
print(schedule)