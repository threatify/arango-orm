"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .data import Person
from arango import ArangoClient
from arango.collections.base import CollectionStatisticsError

from arango_orm.database import Database
from arango_orm.collections import Collection


class TestDatabase(TestBase):

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        db.create_collection(Person)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_collection(Person)

    def test_01_database_object_creation(self):

        db = self._get_db_obj()

        assert isinstance(db, Database)

    def test_02_create_collection(self):

        db = self._get_db_obj()
        new_col = Collection('new_collection')
        db.create_collection(new_col)

        assert db['new_collection'].statistics()

    def test_03_drop_collection(self):
        db = self._get_db_obj()
        new_col = Collection('new_collection')

        assert db['new_collection'].statistics()

        db.drop_collection(new_col)

        with self.assertRaises(CollectionStatisticsError):
            db['new_collection'].statistics()

    def test_04_create_collection_from_custom_class(self):

        db = self._get_db_obj()

        db.drop_collection(Person)

        with self.assertRaises(CollectionStatisticsError):
            db['persons'].statistics()

        db.create_collection(Person)

        assert db['persons'].statistics()

    def test_05_add_records(self):

        db = self._get_db_obj()

        p = Person(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
        db.add(p)

    def test_06_delete_records(self):

        db = self._get_db_obj()

        p = Person(name='temp', _key='73', dob=date(year=2016, month=9, day=12))
        db.add(p)

        count_1 = db.query(Person).count()

        print(p._dump())
        db.delete(p)

        count_2 = db.query(Person).count()

        assert count_2 == count_1 - 1

    def test_07_update_records(self):

        db = self._get_db_obj()

        p = db.query(Person).by_key("12312")
        p.name = 'Anonymous'
        db.update(p)

        p = db.query(Person).by_key("12312")
        assert 'Anonymous' == p.name

    def test_08_raw_aql_and_object_conversion(self):
        db = self._get_db_obj()

        db.add(Person(name='test1', _key='12345', dob=date(year=2016, month=9, day=12)))
        db.add(Person(name='test2', _key='22346', dob=date(year=2015, month=9, day=12)))

        persons = [Person._load(p) for p in db.aql.execute("FOR p IN persons RETURN p")]

        assert len(persons) >= 2
        assert isinstance(persons[0], Person)
