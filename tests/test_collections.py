"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .person import Person
from arango import ArangoClient
from arango.collections.base import CollectionStatisticsError
from arango_orm.database import Database
from arango_orm.collections import Collection


class TestCollection(TestBase):

    def _get_db_obj(self):

        test_db = self.get_db()
        db = Database(test_db)

        return db

    def test_01_object_from_dict(self):

        pd = {'cnic': '37405-4564665-7', 'dob': '2016-09-12', 'name': 'Kashif Iftikhar'}
        new_person = Person._load(pd)

        assert '37405-4564665-7' == new_person.cnic
        assert 'Kashif Iftikhar' == new_person.name
        assert date(year=2016, month=9, day=12) == new_person.dob
        assert '37405-4564665-7' == new_person._key

    def test_02_object_creation(self):

        p = Person(name='test', cnic='12312', dob=date(year=2016, month=9, day=12))
        assert 'test' == p.name
        assert '12312' == p.cnic
        assert date(year=2016, month=9, day=12) == p.dob

    def test_03_object_dump(self):

        p = Person(name='test', cnic='12312', dob=date(year=2016, month=9, day=12))
        d = p._dump()

        assert 'test' == d['name']
        assert '12312' == d['cnic']
        assert '12312' == d['_key']
        assert '2016-09-12' == d['dob']

    def test_04_object_partial_fields_and_dump(self):

        p = Person(name='test', cnic='12312')
        d = p._dump()

        self.assert_all_in(['name', 'cnic', '_key'], d)
        assert 'dob' not in d
