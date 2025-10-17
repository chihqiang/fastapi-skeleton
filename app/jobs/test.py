from boot.celery import queue


@queue.task(name="test_job")
def sample_job():
    print("test_job!")
