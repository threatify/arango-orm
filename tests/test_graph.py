"Test cases for the :module:`arango_orm.database`"

from datetime import date

from arango.exceptions import GraphPropertiesError

from arango_orm.database import Database
from arango_orm.collections import Collection, Relation

from . import TestBase
from .data import (UniversityGraph, Student, Teacher, Subject, SpecializesIn, Area,
                   teachers_data, students_data, subjects_data, specializations_data, areas_data)


class TestGraph(TestBase):

    _graph = None

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        cls._graph = UniversityGraph()
        db.create_graph(cls._graph)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        #db.drop_graph(cls._graph)

    def test_01_graph_and_collections_exist(self):

        db = self._get_db_obj()
        props = db.graph(self._graph.__graph__).properties()

        collection_names = [col['name'] for col in db.collections()]
        uni_graph_collections = [
            'studies', 'specializes_in', 'teaches', 'subjects', 'resides_in', 'areas',
            'students', 'teachers'
        ]

        assert self._graph.__graph__ == props['name']
        self.assert_all_in(uni_graph_collections, collection_names)

    def test_02_data_insertion(self):

        db = self._get_db_obj()

        for s in students_data:
            db.add(s)

        for t in teachers_data:
            db.add(t)

        for s in subjects_data:
            db.add(s)

        for a in areas_data:
            db.add(a)

        for sp in specializations_data:
            db.add(sp)

    def test_03_add_relation_using_graph_relation(self):

        db = self._get_db_obj()

        gotham = db.query(Area).by_key("Gotham")
        metropolis = db.query(Area).by_key("Metropolis")
        star_city = db.query(Area).by_key("StarCity")

        john_wayne = db.query(Student).by_key("S1001")
        lilly_parker = db.query(Student).by_key("S1002")
        cassandra_nix = db.query(Student).by_key("S1003")
        peter_parker = db.query(Student).by_key("S1004")

        intro_to_prog = db.query(Subject).by_key("ITP101")
        comp_history = db.query(Subject).by_key("CS102")
        oop = db.query(Subject).by_key("CSOOP02")

        barry_allen = db.query(Teacher).by_key("T002")
        bruce_wayne = db.query(Teacher).by_key("T001")
        amanda_waller = db.query(Teacher).by_key("T003")

        db.add(self._graph.relation(peter_parker, Relation("studies"), oop))
        db.add(self._graph.relation(peter_parker, Relation("studies"), intro_to_prog))
        db.add(self._graph.relation(john_wayne, Relation("studies"), oop))
        db.add(self._graph.relation(john_wayne, Relation("studies"), comp_history))
        db.add(self._graph.relation(lilly_parker, Relation("studies"), intro_to_prog))
        db.add(self._graph.relation(lilly_parker, Relation("studies"), comp_history))
        db.add(self._graph.relation(cassandra_nix, Relation("studies"), oop))
        db.add(self._graph.relation(cassandra_nix, Relation("studies"), intro_to_prog))

        db.add(self._graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), oop))
        db.add(self._graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), intro_to_prog))
        db.add(self._graph.relation(bruce_wayne, SpecializesIn(expertise_level="medium"), oop))
        db.add(self._graph.relation(bruce_wayne, SpecializesIn(expertise_level="expert"), comp_history))
        db.add(self._graph.relation(amanda_waller, SpecializesIn(expertise_level="basic"), intro_to_prog))
        db.add(self._graph.relation(amanda_waller, SpecializesIn(expertise_level="medium"), comp_history))

        db.add(self._graph.relation(bruce_wayne, Relation("teaches"), oop))
        db.add(self._graph.relation(barry_allen, Relation("teaches"), intro_to_prog))
        db.add(self._graph.relation(amanda_waller, Relation("teaches"), comp_history))

        db.add(self._graph.relation(bruce_wayne, Relation("resides_in"), gotham))
        db.add(self._graph.relation(barry_allen, Relation("resides_in"), star_city))
        db.add(self._graph.relation(amanda_waller, Relation("resides_in"), metropolis))
        db.add(self._graph.relation(john_wayne, Relation("resides_in"), gotham))
        db.add(self._graph.relation(lilly_parker, Relation("resides_in"), metropolis))
        db.add(self._graph.relation(cassandra_nix, Relation("resides_in"), star_city))
        db.add(self._graph.relation(peter_parker, Relation("resides_in"), metropolis))
