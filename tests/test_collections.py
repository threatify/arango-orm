"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .data import Person


class TestCollection(TestBase):

    def test_01_object_from_dict(self):

        pd = {'_key': '37405-4564665-7', 'dob': '2016-09-12', 'name': 'Kashif Iftikhar'}
        new_person = Person._load(pd)

        assert '37405-4564665-7' == new_person._key
        assert 'Kashif Iftikhar' == new_person.name
        assert date(year=2016, month=9, day=12) == new_person.dob
        assert '37405-4564665-7' == new_person._key

    def test_02_object_creation(self):

        p = Person(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
        assert 'test' == p.name
        assert '12312' == p._key
        assert date(year=2016, month=9, day=12) == p.dob

    def test_03_object_dump(self):

        p = Person(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
        d = p._dump()

        print(d)
        assert 'test' == d['name']
        assert '12312' == d['_key']
        assert '12312' == d['_key']
        assert '2016-09-12' == d['dob']

    def test_04_object_partial_fields_and_dump(self):

        p = Person(name='test', _key='12312')
        d = p._dump()

        print(d)
        self.assert_all_in(['name', '_key'], d)
        assert d['dob'] is None
