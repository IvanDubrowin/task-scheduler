from typing import Tuple

from flask import Response, jsonify, request

from server.app import app
from server.exceptions.tasks import InvalidStateError
from server.models import Job, JobGroup
from server.services.tasks import JobsService

job_service = JobsService.get_instance()


@app.route('/tasks/start/<int:job_count>/<int:job_group_id>', methods=['POST'])
def start_jobs(job_count: int, job_group_id: int) -> Tuple[Response, int]:
    """
    запуск N джобов для группы с идентификатором <job_group_id> (некое целое положительное число)
    """
    job_service.start_jobs(job_count, job_group_id)
    return jsonify({'success': f'Run {job_count} jobs for group {job_group_id}'}), 201


@app.route('/tasks/groups', methods=['GET'])
def get_job_groups() -> Response:
    """
    список групп, output: {<job_group_id>: <число джобов в группе со статусом running>}
    """
    return jsonify(job_service.get_job_groups())


@app.route('/tasks/', methods=['GET'])
def get_jobs() -> Response:
    """
    список всех джобов; опционально сделать фильтр для вывода джобов с определенным состоянием (?state=xxx)
    """
    state = request.args.get('state')
    queryset = Job.query.filter(Job.state.isnot(None))

    if state and Job.is_valid_state(state):
        queryset = queryset.filter(Job.state == state)

    return jsonify([job.to_dict() for job in queryset.all()])


@app.route('/tasks/<int:job_group_id>', methods=['GET'])
def get_jobs_by_group(job_group_id: int) -> Response:
    """
    список всех джобов в группе <job_group_id>;
    опционально сделать фильтр для вывода джобов с определенным состоянием (?state=xxx)
    """
    state = request.args.get('state')
    queryset = Job.query \
        .filter_by(group_id=job_group_id) \
        .filter(Job.state.isnot(None))

    if state and Job.is_valid_state(state):
        queryset = queryset.filter(Job.state == state)

    return jsonify([job.to_dict() for job in queryset.all()])


@app.route('/tasks/<int:job_id>', methods=['DELETE'])
def revoke_job(job_id: int) -> Tuple[Response, int]:
    """
    прерывание джоба с идентификатором <job_id>
    """
    try:
        job = Job.query.get_or_404(job_id)
        job_service.revoke_job(job)
        return jsonify({'success': f'Revoke job {job_id}'}), 200
    except InvalidStateError:
        return jsonify({'error': 'Invalid job status'}), 400


@app.route('/tasks/group/<int:job_group_id>', methods=['DELETE'])
def revoke_jobs_by_group(job_group_id: int) -> Response:
    """
    прерывание запущенных джобов в группе <job_group_id>
    """
    group = JobGroup.query.get_or_404(job_group_id)
    job_service.revoke_jobs_by_group(group)
    return jsonify({'success': f'Revoke jobs by group {job_group_id}'})
