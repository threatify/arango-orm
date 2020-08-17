import logging
import os

import pytest
from arango import ArangoClient
from arango.exceptions import DatabaseCreateError

log = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_database_test(request):
    username = os.environ.get('ARANGO_USERNAME', "test")
    password = os.environ.get('ARANGO_PASSWORD', "test")
    arango_hosts = os.environ.get('ARANGO_HOSTS', "http://arangodb:8529")
    database_name = os.environ.get('ARANGO_DATABASE', "test")

    sys_db = ArangoClient(hosts=arango_hosts).db('_system', username=username, password=password)
    try:
        sys_db.create_database(database_name)
    except DatabaseCreateError as exp:
        log.info("Could not create the test db, probably already exists. %s", str(exp))

    yield
