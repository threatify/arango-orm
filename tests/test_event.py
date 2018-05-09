from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from datetime import date
from arango_orm.event import dispatch, listen, listens_for
from arango_orm import Collection
if sys.version >= '3.6':
    # Since assert_called_once is wew in version 3.6
    from unittest.mock import create_autospec, Mock
else:
    from mock import create_autospec, Mock

from . import TestBase
from .data import Person


class BasePerson(object):
    pass


class MyPerson(BasePerson):
    def __init__(self, name):
        self.name = name

    def sleep(self):
        dispatch(self, 'gone_sleep')


class TestCollection(TestBase):
    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        db.create_collection(Person)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_collection(Person)

    def _gone_sleep_notification(self, target, event, *args, **kwargs):
        print('{0} has got in sleep~'.format(target.name))

    def test_event_works(self):
        mock_listener = create_autospec(self._gone_sleep_notification)

        listen(MyPerson, 'gone_sleep', self._gone_sleep_notification)
        listen(MyPerson, 'gone_sleep', mock_listener)

        p = MyPerson('Wonder')
        p.sleep()

        mock_listener.assert_called_once_with(p, 'gone_sleep')

    def test_listen_by_base_class(self):
        mock = Mock()

        listen(BasePerson, 'gone_sleep', mock)

        p = MyPerson('James')
        p.sleep()

        mock.assert_called_once()  # only available in python 3.6 for builtin unittest.mock

    def test_listens_for_decorator(self):
        mock = Mock()

        @listens_for(MyPerson, 'gone_sleep')
        def gone_sleep_handler(*args, **kwargs):
            mock(*args, **kwargs)

        p = MyPerson('Wonder')
        p.sleep()
        mock.assert_called_once()  # only available in python 3.6 for builtin unittest.mock

    def test_orm_events(self):
        ma, mu, md = Mock(), Mock(), Mock()

        listen(Person, 'post_add', ma)
        listen(Person, 'post_update', mu)
        listen(Person, 'post_delete', md)

        p = Person(name='Wonder', _key='10000', dob=date(year=2016, month=9, day=12))

        res = self.db.add(p)
        ma.assert_called_once_with(p, 'post_add', db=self.db, result=res)

        res = self.db.update(p)
        mu.assert_called_once_with(p, 'post_update', db=self.db, result=res)
        res = self.db.update(p)
        assert mu.call_count == 2

        res = self.db.delete(p)
        md.assert_called_once_with(p, 'post_delete', db=self.db, result=res)
