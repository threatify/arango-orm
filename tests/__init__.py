import unittest
import logging
from arango import ArangoClient
from arango_orm.database import Database

from .utils import lazy_property

log = logging.getLogger(__name__)


class TestBase(unittest.TestCase):
    "Base class for test cases (unit tests)"

    client = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            cls.client = ArangoClient()

        return cls.client

    @classmethod
    def get_db(cls):
        return cls.get_client().db('test', username='test', password='test')

    @classmethod
    def _get_db_obj(cls):

        test_db = cls.get_db()
        db = Database(test_db)

        return db

    @lazy_property
    def db(self):
        return TestBase._get_db_obj()

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

    def assert_has_same_items(self, left, right, exp_to_raise=AssertionError):
        if not set(left) == set(right):
            raise exp_to_raise
        return True
