"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .person import Person
from arango import ArangoClient
from arango.collections.base import CollectionStatisticsError

from arango_orm.database import Database
from arango_orm.collections import Collection


class TestDatabase(TestBase):

    def _get_db_obj(self):

        test_db = self.get_db()
        db = Database(test_db)

        return db

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
