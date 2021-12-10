"Test cases for the :module:`arango_orm.database`"

from datetime import date

from arango.exceptions import GraphPropertiesError

from arango_orm.database import Database
from arango_orm.collections import Collection, Relation

from . import TestBase
from .data import (UniversityGraph, Student, Teacher, Subject, SpecializesIn, Area,
                   teachers_data, students_data, subjects_data, specializations_data, areas_data)


class TestInFiltering(TestBase):

    _graph = None

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        cls._graph = UniversityGraph(connection=db)
        db.create_graph(cls._graph)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_graph(cls._graph)

    def test_01_in_filtering(self):

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

        filtered_students = db.query(Student).filter_by(age=[20, 30]).all()

        assert 2 == len(filtered_students)
        for student in filtered_students:
            assert "John Wayne" == student.name or "Peter Parker" == student.name
