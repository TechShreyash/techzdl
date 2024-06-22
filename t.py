import asyncio

async def some_task(name, duration):
    try:
        print(f"Task {name} started")
        await asyncio.sleep(duration)
        if name == "task2":
            raise ValueError(f"Exception in {name}")
        print(f"Task {name} completed")
    except asyncio.CancelledError:
        print(f"Task {name} was cancelled")
        raise

async def main():
    tasks = []
    task_names = ["task1", "task2", "task3"]
    durations = [5, 2, 4]  # Durations for each task

    # Create tasks
    for name, duration in zip(task_names, durations):
        tasks.append(asyncio.create_task(some_task(name, duration)))

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Check for exceptions in the completed tasks
    for task in done:
        if task.exception():
            print(f"Exception occurred: {task.exception()}")
            for pending_task in pending:
                pending_task.cancel()
            # Wait for the cancellation to complete
            await asyncio.gather(*pending, return_exceptions=True)
            break

    # Report on task statuses
    for task in tasks:
        if task.cancelled():
            print(f"{task.get_name()} was cancelled")
        elif task.exception():
            print(f"{task.get_name()} raised an exception: {task.exception()}")
        else:
            print(f"{task.get_name()} completed successfully")

# Run the main function
asyncio.run(main())
