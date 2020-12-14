"Test cases for the :module:`arango_orm.database`"

from . import TestBase
from .data import PeopleGraph, people_data, People, Father, Mother, Son, Daughter


class TestInheritanceMultiple(TestBase):

    _graph = None

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        cls._graph = PeopleGraph(connection=db)
        db.create_graph(cls._graph)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_graph(cls._graph)

    def test_01_node_expansion_inheritance_with_mapping_resolver(self):
        db = self.__class__._get_db_obj()

        for person in people_data:
            db.add(person)

        homer = db.query(Father).by_key("001")

        assert homer.name == 'Homer'
        assert homer.work == 'Nuclear supervisor'
        assert homer.personality == 'lazy'
        assert homer.wife_name == 'Marge'

        marge = db.query(Mother).by_key("002")

        assert marge.name == 'Marge'
        assert marge.work == 'None'
        assert marge.hair_color == 'blue'
        assert marge.husband_name == 'Homer'

        bart = db.query(Son).by_key("003")

        assert bart.name == 'Bart'
        assert bart.hobby == 'Skateboard'
        assert bart.personality == 'playful'
        assert bart.sister_name == 'Lisa'

        lisa = db.query(Daughter).by_key("004")

        assert lisa.name == 'Lisa'
        assert lisa.hobby == 'Saxophone'
        assert lisa.hair_color == 'yellow'
        assert lisa.brother_name == 'Bart'
