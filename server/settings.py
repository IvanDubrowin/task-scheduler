import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

TEST_DB_PATH = os.path.join(BASE_DIR, 'test.db')

SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI', 'sqlite:///' + TEST_DB_PATH)

MIN_TASK_SLEEP = int(os.getenv('MIN_TASK_SLEEP', 3))

MAX_TASK_SLEEP = int(os.getenv('MAX_TASK_SLEEP', 6))

SCHEDULER_THREAD_COUNT = int(os.getenv('SCHEDULER_THREAD_COUNT', os.cpu_count() or 1 * 4))
