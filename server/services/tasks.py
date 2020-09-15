import logging
import random
from datetime import datetime
from typing import Dict, List, Optional

from server.app import db, scheduler
from server.exceptions.tasks import InvalidStateError
from server.models import Job, JobGroup
from server.models.tasks import JobState
from server.settings import MAX_TASK_SLEEP, MIN_TASK_SLEEP

logger = logging.getLogger(__name__)


class JobsService:
    """
    Сервис фоновых задач
    """
    instance: Optional['JobsService'] = None

    def __init__(self) -> None:
        self.scheduler = scheduler

    def start_jobs(self, job_count: int, job_group_id: int) -> None:
        """
        Запуск заданий
        """
        group: JobGroup = JobGroup.get_or_create(id=job_group_id)
        for _ in range(job_count):
            job = Job.create(group_id=group.id)
            self.scheduler.add_job(
                job.start,
                'interval',
                minutes=random.randint(MIN_TASK_SLEEP, MAX_TASK_SLEEP),
                id=str(job.id)
            )

    def revoke_job(self, job: Job) -> None:
        """
        Отмена задания
        """
        if job.is_stopped:
            raise InvalidStateError

        self.scheduler.remove_job(str(job.id))
        job.update(state=JobState.CANCELED, end_time=datetime.now())
        logger.debug(f'Job {job.id} canceled')

    def revoke_jobs_by_group(self, group: JobGroup) -> None:
        """
        Отмена всех заданий группы
        """
        jobs = Job.query.filter_by(group_id=group.id, state=JobState.RUNNING).all()
        for job in jobs:
            self.scheduler.remove_job(str(job.id))
            job.update(state=JobState.CANCELED, end_time=datetime.now())
            logger.debug(f'Job {job.id} canceled')

    @staticmethod
    def get_job_groups() -> List[Dict[str, int]]:
        result = []
        queryset = db.session \
            .query(JobGroup.id, db.func.count(Job.id)) \
            .outerjoin(Job) \
            .having(Job.state == JobState.RUNNING) \
            .group_by(JobGroup, Job.state) \
            .all()
        for group_id, running_jobs_count in queryset:
            result.append({
                'job_group_id': group_id,
                'running_jobs': running_jobs_count
            })
        return result

    @classmethod
    def get_instance(cls) -> 'JobsService':
        if not cls.instance:
            cls.instance = JobsService()
            return cls.instance
        return cls.instance
