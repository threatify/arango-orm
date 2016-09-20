"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .person import Person
from arango import ArangoClient
from arango.collections.base import CollectionStatisticsError

from arango_orm.database import Database
from arango_orm.collections import Collection


class TestDatabase(TestBase):


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
        db.create_collection(Person)

        assert db['persons'].statistics()

        db.drop_collection(Person)

        with self.assertRaises(CollectionStatisticsError):
            db['persons'].statistics()

    def test_05_add_records(self):

        db = self._get_db_obj()
        db.create_collection(Person)
        p = Person(name='test', cnic='12312', dob=date(year=2016, month=9, day=12))
        db.add(p)
        db.drop_collection(Person)

    def test_06_raw_aql_and_object_conversion(self):
        db = self._get_db_obj()
        db.create_collection(Person)
        db.add(Person(name='test1', cnic='12312', dob=date(year=2016, month=9, day=12)))
        db.add(Person(name='test2', cnic='22312', dob=date(year=2015, month=9, day=12)))

        persons = [Person._load(p) for p in db.aql.execute("FOR p IN persons RETURN p")]

        assert len(persons) == 2
        assert isinstance(persons[0], Person)

        db.drop_collection(Person)
