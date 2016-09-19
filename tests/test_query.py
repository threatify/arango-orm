"Test cases for the :module:`arango_orm.database`"

from datetime import date
from . import TestBase
from .person import Person
from arango import ArangoClient
from arango.collections.base import CollectionStatisticsError

from arango_orm.database import Database
from arango_orm.collections import Collection
from arango_orm.query import Query


class TestQuery(TestBase):

    def _get_db_obj(self):

        test_db = self.get_db()
        db = Database(test_db)

        return db

    def _create_persons_collection(self):

        db = self._get_db_obj()
        db.create_collection(Person)

    def test_01_get_count(self):

        db = self._get_db_obj()

        self._create_persons_collection()

        count_1 = db.query(Person).count()
        assert count_1 == 0

    def test_02_get_all_records(self):
        db = self._get_db_obj()

        count_1 = db.query(Person).count()
        db.add(Person(name='test1', cnic='12312', dob=date(year=2016, month=9, day=12)))
        db.add(Person(name='test2', cnic='22312', dob=date(year=2015, month=9, day=12)))

        assert db.query(Person).count() == count_1 + 2

        persons = db.query(Person).all()
        assert len(persons) == 2
        assert isinstance(persons[0], Person)

        db.drop_collection(Person)
