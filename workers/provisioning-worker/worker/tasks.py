import time

from worker.celery_app import celery_app
from worker.db import SessionLocal

from app.models.job import Job


@celery_app.task(name="process_create_service_job")
def process_create_service_job(job_id: str):
    """
    Simulates long-running control-plane provisioning workflow.
    Updates job lifecycle:
    PENDING -> RUNNING -> SUCCEEDED
    """
    db = SessionLocal()

    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()

        if not job:
            print(f"[Celery] Job not found: {job_id}")
            return

        print(f"[Celery] Starting job: {job_id}")

        # Step 1: mark job running
        job.state = "RUNNING"
        db.commit()

        # Step 2: simulate slow provisioning workflow
        time.sleep(5)

        # Step 3: mark job success
        job.state = "SUCCEEDED"
        db.commit()

        print(f"[Celery] Completed job: {job_id}")

    except Exception as exc:
        print(f"[Celery] Failed job {job_id}: {exc}")
        db.rollback()

        if job:
            job.state = "FAILED"
            db.commit()

        raise

    finally:
        db.close()