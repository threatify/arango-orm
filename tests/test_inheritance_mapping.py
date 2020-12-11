"Test cases for the :module:`arango_orm.database`"

from . import TestBase
from .data import (OwnershipGraph, Owner, Bike, Truck, owner_data, vehicle_data, own_data)


class TestInheritanceMapping(TestBase):

    _graph = None

    @classmethod
    def setUpClass(cls):
        db = cls._get_db_obj()
        cls._graph = OwnershipGraph(connection=db)
        db.create_graph(cls._graph)

    @classmethod
    def tearDownClass(cls):
        db = cls._get_db_obj()
        db.drop_graph(cls._graph)

    def test_01_node_expansion_inheritance_with_discriminator_mapping(self):

        db = self._get_db_obj()

        for owner in owner_data:
            db.add(owner)

        for vehicle in vehicle_data:
            db.add(vehicle)

        for ownership in own_data:
            db.add(ownership)

        john = db.query(Owner).by_key("001")

        self._graph.expand(john)

        vehicles = [relation._object_to for relation in john._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Bike)

        billy = db.query(Owner).by_key("002")

        self._graph.expand(billy)

        vehicles = [relation._object_to for relation in billy._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Truck)

        luke = db.query(Owner).by_key("003")

        self._graph.expand(luke)

        vehicles = [relation._object_to for relation in luke._relations['own']]
        for vehicle in vehicles:
            assert isinstance(vehicle, Bike) or isinstance(vehicle, Truck)
