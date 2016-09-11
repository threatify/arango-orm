import unittest
import logging
from arango import ArangoClient

log = logging.getLogger(__name__)

class TestBase(unittest.TestCase):
    "Base class for test cases (unit tests)"

    client = None

    def get_client(self):
        if self.client is None:
            self.client = ArangoClient(username='test', password='test')

        return self.client

    def get_db(self):
        return self.get_client().db('test')

    def assert_all_in(self, keys, collection, exp_to_raise=AssertionError):
        "Assert that all given keys are present in the given collection, dict, list or tuple"

        for key in keys:
            if key not in collection:
                raise exp_to_raise

        return True

    def assert_any_in(self, keys, collection, exp_to_raise=AssertionError):
        "Assert that any of the given keys is present in the given collection, dict, list or tuple"

        for key in keys:
            if key in collection:
                return True

        raise exp_to_raise

    def assert_none_in(self, keys, collection, exp_to_raise=AssertionError):
        "Assert that none of the given keys is present in the given collection, dict, list or tuple"

        for key in keys:
            if key in collection:
                raise exp_to_raise

        return True
