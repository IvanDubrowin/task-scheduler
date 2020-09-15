import json

from flask.testing import FlaskClient
from flask.wrappers import Response

from server.models import Job
from server.models.tasks import JobState


def test_start_jobs(client: FlaskClient) -> None:
    response: Response = client.get('/tasks/start/2/5/')
    assert response.status_code == 405

    response: Response = client.post('/tasks/start/2/5/')
    assert response.status_code == 201
    assert json.loads(response.data) == {"success": "Run 2 jobs for group 5"}


def test_get_job_groups(client: FlaskClient) -> None:
    response: Response = client.post('/tasks/groups/')
    assert response.status_code == 405

    response: Response = client.get('/tasks/groups/')
    assert response.status_code == 200
    assert json.loads(response.data) == [{"job_group_id": 5, "running_jobs": 2}]


def test_get_jobs(client: FlaskClient) -> None:
    response: Response = client.post('/tasks/')
    assert response.status_code == 405

    response: Response = client.get('/tasks/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['group_id'] == 5
    assert data[0]['state'] == JobState.RUNNING
    assert not data[0]['end_time']

    response: Response = client.get('/tasks/?state=completed')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0


def test_get_jobs_by_group(client: FlaskClient) -> None:
    response: Response = client.post('/tasks/1/')
    assert response.status_code == 405

    response: Response = client.get('/tasks/1/')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0

    response: Response = client.get('/tasks/5/')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 2

    response: Response = client.get('/tasks/5/?state=completed')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 0


def test_revoke_job(client: FlaskClient) -> None:
    response: Response = client.get('/tasks/')
    assert response.status_code == 200

    data = json.loads(response.data)
    nonexistent_job_id = 2452424242
    job_id = data[0]['id']
    response: Response = client.delete(f'/tasks/{nonexistent_job_id}/')
    assert response.status_code == 404
    response: Response = client.delete(f'/tasks/{job_id}/')
    assert response.status_code == 200

    job = Job.query.filter_by(id=job_id).first()
    assert job.id == job_id
    assert job.state == JobState.CANCELED

    response: Response = client.delete(f'/tasks/{job_id}/')
    assert response.status_code == 400


def test_revoke_jobs_by_group(client: FlaskClient) -> None:
    nonexistent_group_id = 2452424242
    response: Response = client.delete(f'f/tasks/group/{nonexistent_group_id}/')
    assert response.status_code == 404

    response: Response = client.delete('/tasks/group/5/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {'success': 'Revoke jobs by group 5'}
