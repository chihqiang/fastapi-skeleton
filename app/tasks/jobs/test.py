from boot.celery import app


@app.task(name="test_job")
def sample_job():
    print("test_job!")
