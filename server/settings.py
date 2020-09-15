import os

SECRET_KEY = os.getenv('SECRET_KEY')

SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI')

MIN_TASK_SLEEP = int(os.getenv('MIN_TASK_SLEEP', 3))

MAX_TASK_SLEEP = int(os.getenv('MAX_TASK_SLEEP', 6))

SCHEDULER_THREAD_COUNT = int(os.getenv('SCHEDULER_THREAD_COUNT', os.cpu_count() or 1 * 4))
