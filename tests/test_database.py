"Test cases for the :module:`arango_orm.database`"

import logging
from datetime import date
from arango.exceptions import CollectionStatisticsError
from arango_orm.database import Database
from arango_orm.graph import GraphConnection
from arango_orm.collections import Collection

from . import TestBase
from .data import (Person, UniversityGraph, Student, Teacher, Subject, SpecializesIn, Area,
                   DummyFromCol1, DummyFromCol2, DummyRelation, DummyToCol1, DummyToCol2)

log = logging.getLogger(__name__)


class TestDatabase(TestBase):

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        if not db.has_collection(Person):
            db.create_collection(Person)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        if db.has_collection(Person):
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

        p = Person(name='test', _key='12312', age=18, dob=date(year=2016, month=9, day=12))
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

    def test_09_add_record_with_auto_key(self):

        db = self._get_db_obj()

        p = Person(name='key less', dob=date(year=2016, month=9, day=12))
        db.add(p)

    def _get_graph(self):
        db = self._get_db_obj()
        return (db, UniversityGraph(connection=db))

    def test_10_create_graph(self):
        db, graph = self._get_graph()
        db.create_graph(graph)

        assert graph.__graph__ in [g['name'] for g in db.graphs()]

    def test_11_update_graph_add_connection(self):

        UniversityGraph.graph_connections.append(
            GraphConnection(DummyFromCol1, DummyRelation, DummyToCol1)
        )

        assert 5 == len(UniversityGraph.graph_connections)

        db, graph = self._get_graph()
        db.update_graph(graph)

        # Test if we have the new collections and graph relation
        col_names = [c['name'] for c in db.collections()]

        assert DummyFromCol1.__collection__ in col_names
        assert DummyToCol1.__collection__ in col_names
        assert DummyRelation.__collection__ in col_names

        assert DummyFromCol2.__collection__ not in col_names
        assert DummyToCol2.__collection__ not in col_names

        gi = db.graphs()[0]
        log.debug(gi)

        assert DummyRelation.__collection__ in [e['edge_collection'] for e in gi['edge_definitions']]

    def test_12_update_graph_update_connection(self):

        UniversityGraph.graph_connections[-1] = GraphConnection(
            [DummyFromCol1, DummyFromCol2], DummyRelation, [DummyToCol1, DummyToCol2]
        )

        assert 5 == len(UniversityGraph.graph_connections)
        db, graph = self._get_graph()
        db.update_graph(graph)

        # Test if we have the new collections and graph relation
        col_names = [c['name'] for c in db.collections()]

        assert DummyFromCol1.__collection__ in col_names
        assert DummyFromCol2.__collection__ in col_names
        assert DummyToCol1.__collection__ in col_names
        assert DummyToCol2.__collection__ in col_names
        assert DummyRelation.__collection__ in col_names

        gi = db.graphs()[0]
        assert DummyRelation.__collection__ in [e['edge_collection'] for e in gi['edge_definitions']]

    def test_13_update_graph_remove_connection(self):

        # Remove the dummy relation connection
        UniversityGraph.graph_connections.pop()
        assert 4 == len(UniversityGraph.graph_connections)

        db, graph = self._get_graph()
        db.update_graph(graph)

        # Test if we have the new collections and graph relation
        col_names = [c['name'] for c in db.collections()]

        # Verify that the collections still exist
        assert DummyFromCol1.__collection__ in col_names
        assert DummyFromCol2.__collection__ in col_names
        assert DummyToCol1.__collection__ in col_names
        assert DummyToCol2.__collection__ in col_names
        assert DummyRelation.__collection__ in col_names

        gi = db.graphs()[0]
        assert DummyRelation.__collection__ not in [e['edge_collection'] for e in gi['edge_definitions']]

    def test_14_drop_graph_without_collections(self):
        db, graph = self._get_graph()
        db.drop_graph(graph, drop_collections=False)

        # verify that the collections are not deleted
        assert 'teaches' in [c['name'] for c in db.collections()]

    def test_15_drop_graph_with_collections(self):
        # making sure we remove the dummy collections too
        UniversityGraph.graph_connections.append(GraphConnection(
            [DummyFromCol1, DummyFromCol2], DummyRelation, [DummyToCol1, DummyToCol2]
        ))
        db, graph = self._get_graph()
        db.create_graph(graph)
        db.drop_graph(graph, drop_collections=True)

        # verify that the collections are not deleted
        assert 'teaches' not in [c['name'] for c in db.collections()]

        # Remove the dummy relation connection
        UniversityGraph.graph_connections.pop()

    def test_16_create_all(self):

        db_objects = [UniversityGraph, DummyFromCol1, DummyToCol1]
        db = self._get_db_obj()
        db.create_all(db_objects)

        # confirm that graph was created
        assert len(db.graphs()) > 0
        assert db.graphs()[0]['name'] == UniversityGraph.__graph__

        col_names = [c['name'] for c in db.collections()]
        # Confrim dummy from col 1 and to col 2 are created and other dummy collections are not
        # created by the create_all call
        assert DummyFromCol1.__collection__ in col_names
        assert DummyToCol1.__collection__ in col_names

        assert DummyFromCol2.__collection__ not in col_names
        assert DummyToCol2.__collection__ not in col_names
        assert DummyRelation.__collection__ not in col_names

        # Confirm all graph collections are craeted
        assert Student.__collection__ in col_names
        assert Teacher.__collection__ in col_names
        assert Subject.__collection__ in col_names
        assert SpecializesIn.__collection__ in col_names
        assert Area.__collection__ in col_names

        # Now drop the graph and any remaining collections
        db, graph = self._get_graph()
        db.drop_graph(graph, drop_collections=True)
        db.drop_collection(DummyFromCol1)
        db.drop_collection(DummyToCol1)

    def test_17_default_field_value(self):
        db = self._get_db_obj()

        p = db.query(Person).by_key("12312")

        assert p.is_staff is False  # not None

    def test_18_nodirty_from_db(self):
        db = self._get_db_obj()

        p = db.query(Person).by_key("12312")
        assert not p._dirty

        p.name = 'Anonymous'
        self.assert_has_same_items(p._dirty, {'name'})

    def test_19_nodirty_after_save(self):
        db = self._get_db_obj()

        p = db.query(Person).by_key("12312")
        p.name = 'NB'
        self.assert_has_same_items(p._dirty, {'name'})
        db.update(p)
        assert not p._dirty

        new_p = Person(name='test1', dob=date(year=2016, month=9, day=12))
        assert len(new_p._dirty)
        db.add(new_p)
        assert not new_p._dirty

    def test_20_only_save_dirty_fields(self):
        db = self._get_db_obj()

        # We keep two references of the same record from db
        p_ref1 = db.query(Person).by_key("12312")
        p_ref2 = db.query(Person).by_key("12312")

        # First, let's watch the normal behavior
        p_ref1.name = 'NB-1'
        db.update(p_ref1)   # stmt1
        db.update(p_ref2)   # stmt2

        # stmt2 updated the record with an old value, overrode stmt1's result
        fresh = db.query(Person).by_key("12312")
        assert fresh.name == 'NB'

        # Then, let's do update of only dirty fields
        p_ref1.name = 'NB-1'
        p_ref1.age = 98
        p_ref2.age = 99
        db.update(p_ref1)
        db.update(p_ref2, only_dirty=True)
        fresh = db.query(Person).by_key("12312")
        assert fresh.name == 'NB-1'
        assert fresh.age == 99
