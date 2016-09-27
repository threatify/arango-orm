"Test cases for the :module:`arango_orm.database`"

from datetime import date

from arango.exceptions import GraphPropertiesError

from arango_orm.database import Database
from arango_orm.collections import Collection, Relation

from . import TestBase
from .data import (UniversityGraph, Student, Teacher, Subject, SpecializesIn, Area,
                   teachers_data, students_data, subjects_data, specializations_data)


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

        for sp in specializations_data:
            db.add(sp)

    def test_03_add_relation_using_graph_relation(self):

        db = self._get_db_obj()

        peter_parker = db.query(Student).by_key("S1004")
        oop = db.query(Subject).by_key("CSOOP02")

        db.add(self._graph.relation(peter_parker, Relation("studies"), oop))

        barry_allen = db.query(Teacher).by_key("T002")
        db.add(self._graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), oop))
