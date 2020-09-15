import logging
from datetime import datetime
from enum import Enum
from typing import Any, Type

from server.app import db, scheduler

logger = logging.getLogger(__name__)


class JobState(str, Enum):
    running: str = 'running'
    completed: str = 'completed'
    canceled: str = 'canceled'


class CRUDMixin:
    @classmethod
    def create(cls: Type[db.Model], **kwargs) -> db.Model:
        instance = cls(**kwargs)
        return instance.save()

    def update(self: db.Model, commit: bool = True, **kwargs) -> db.Model:
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self: db.Model, commit: bool = True) -> db.Model:
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self: db.Model, commit: bool = True) -> bool:
        db.session.delete(self)
        return commit and db.session.commit()

    @classmethod
    def get_or_create(cls: Type[db.Model], **kwargs) -> db.Model:
        instance = db.session.query(cls).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance


class JobGroup(db.Model, CRUDMixin):
    """
    Группа задач
    """
    __tablename__ = 'job_groups'
    id = db.Column(db.Integer, primary_key=True)
    jobs = db.relationship('Job', backref='group', lazy='dynamic')

    def __repr__(self) -> str:
        return f'JobGroup {self.id}'


class Job(db.Model, CRUDMixin):
    """
    Задача
    """
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(JobGroup.id))
    state = db.Column(db.Enum(JobState), default=JobState.running)
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f'Job {self.id} state: {self.state}'

    @property
    def is_stopped(self) -> bool:
        return self.state in [JobState.canceled, JobState.completed]

    @staticmethod
    def is_valid_state(value: Any) -> bool:
        states = [item.value for item in JobState]
        return value in states

    def start(self) -> None:
        self.update(state=JobState.completed, end_time=datetime.now())
        logger.debug(f'Job {self.id} in state {self.state}')
        scheduler.remove_job(str(self.id))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'group_id': self.group_id,
            'state': self.state,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
