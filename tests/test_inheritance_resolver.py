"Test cases for the :module:`arango_orm.database`"

from . import TestBase
from .data import (OwnershipGraph2, owner_data2, vehicle_data2, own_data2, Owner2, Bike2, Truck2)


class TestInheritanceResolver(TestBase):

    _graph = None

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        cls._graph = OwnershipGraph2(connection=db)
        db.create_graph(cls._graph)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_graph(cls._graph)

    def test_01_node_expansion_inheritance_with_mapping_resolver(self):
        db = self.__class__._get_db_obj()

        for owner in owner_data2:
            db.add(owner)

        for vehicle in vehicle_data2:
            db.add(vehicle)

        for ownership in own_data2:
            db.add(ownership)

        john = db.query(Owner2).by_key("001")

        self._graph.expand(john)

        vehicles = [relation._object_to for relation in john._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Bike2)

        billy = db.query(Owner2).by_key("002")

        self._graph.expand(billy)

        vehicles = [relation._object_to for relation in billy._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Truck2)

        luke = db.query(Owner2).by_key("003")

        self._graph.expand(luke)

        vehicles = [relation._object_to for relation in luke._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Bike2) or isinstance(vehicle, Truck2)
