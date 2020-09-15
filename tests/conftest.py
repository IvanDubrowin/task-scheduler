import os

import pytest
from flask.testing import FlaskClient

from server import app
from server.settings import TEST_DB_PATH


@pytest.fixture(scope='session')
def client() -> FlaskClient:
    app.config['TESTING'] = True
    os.system('cd server && flask db upgrade')
    with app.test_client() as client:
        yield client
    os.remove(TEST_DB_PATH)
