import logging
import os

import pytest
from arango import ArangoClient

log = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_database_test(request):
    username = os.environ.get('ARANGO_USERNAME', "test")
    password = os.environ.get('ARANGO_PASSWORD', "test")
    arango_ip = os.environ.get('ARANGO_IP', "http://arangodb:8529")
    database_name = os.environ.get('ARANGO_DATABASE', "test")

    sys_db = ArangoClient(hosts=arango_ip).db('_system', username=username, password=password)
    sys_db.create_database(database_name)
    yield
