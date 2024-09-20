from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import atexit

scheduler = BackgroundScheduler()
scheduler.start()

# 确保在程序退出时关闭调度器
atexit.register(lambda: scheduler.shutdown())

def add_job(job_id, func, trigger, **trigger_args):
    scheduler.add_job(func, trigger, id=job_id, **trigger_args)

def remove_job(job_id):
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        print(f"Job {job_id} not found")

def get_jobs():
    return scheduler.get_jobs()