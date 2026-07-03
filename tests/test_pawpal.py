from pawpal_system import Pet, Task


def test_mark_completed_changes_status():
    task = Task(name="Feed Buddy", duration=15)
    assert task.completion_status == "pending"

    task.mark_completed()

    assert task.completion_status == "completed"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Walk Buddy", duration=30))

    assert len(pet.tasks) == 1
