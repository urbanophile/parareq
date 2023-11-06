from parareq.rate_limiter import Job, JobManager
import random
import time


def example_task(task_desc: int):
    randval = random.randint(1, 5)
    print(f"starting__task: {task_desc}")
    time.sleep(randval)
    print(f"finishing_task: {task_desc}")
    return randval


def main_prod():
    # Example usage:
    manager = JobManager(
        call_rate=5.0,
        call_per=8.0,
        token_rate=5.0,
        token_per=8.0,
        total_timeout=10.0,
    )

    # Simulate task queuing
    for task_desc in range(10):
        job = Job(id=task_desc, args={"task_desc": task_desc}, function=example_task)
        manager.add_job(job)

    # Simulate task processing from the queue
    manager.start_jobs()
