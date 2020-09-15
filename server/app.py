from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pytz import utc

from server.settings import SCHEDULER_THREAD_COUNT, SQLALCHEMY_DATABASE_URI

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object('server.settings')
migrate = Migrate(app, db)

jobstores = {
    'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
}
executors = {
    'default': ThreadPoolExecutor(SCHEDULER_THREAD_COUNT)
}
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    timezone=utc,
    daemon=True
)
scheduler.start()
