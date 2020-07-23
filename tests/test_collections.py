"Test cases for the :module:`arango_orm.database`"

from datetime import date
from arango_orm import CollectionBase, Collection
from arango_orm.fields import String, Integer, Dict, DateTime, Nested, List

from . import TestBase
from .data import Person, Car


class TestCollection(TestBase):
    def test_01_object_from_dict(self):
        pd = {
            "_key": "37405-4564665-7",
            "dob": "2016-09-12",
            "name": "Kashif Iftikhar",
        }
        new_person = Person._load(pd)

        assert "37405-4564665-7" == new_person._key
        assert "Kashif Iftikhar" == new_person.name
        assert date(year=2016, month=9, day=12) == new_person.dob
        assert "37405-4564665-7" == new_person._key

    def test_02_object_creation(self):
        p = Person(
            name="test", _key="12312", dob=date(year=2016, month=9, day=12)
        )
        assert "test" == p.name
        assert "12312" == p._key
        assert date(year=2016, month=9, day=12) == p.dob

    def test_03_object_dump(self):
        p = Person(
            name="test", _key="12312", dob=date(year=2016, month=9, day=12)
        )
        d = p._dump()

        print(d)
        assert "test" == d["name"]
        assert "12312" == d["_key"]
        assert "12312" == d["_key"]
        assert "2016-09-12" == d["dob"]

    def test_03_01_object_dump_only(self):
        p = Person(
            name="test", _key="12312", dob=date(year=2016, month=9, day=12)
        )
        only_fields = ["_key", "name"]
        d = p._dump(only=only_fields)

        self.assert_has_same_items(only_fields, d.keys())

    def test_04_object_partial_fields_and_dump(self):
        p = Person(name="test", _key="12312")
        d = p._dump()

        print(d)
        self.assert_all_in(["name", "_key"], d)
        assert d["dob"] is None

    def test_05_object_load_and_dump_with_extra_fields_disabled(self):
        d = {
            "_key": "person_1",
            "name": "John Doe",
            "dob": "2016-09-12",
            "profession": "absent",
        }
        p = Person._load(d)

        assert hasattr(p, "_key")
        assert hasattr(p, "name")
        assert hasattr(p, "dob")
        assert hasattr(p, "profession") is False

        d2 = p._dump()
        self.assert_all_in(["_key", "name", "dob"], d2)
        assert "profession" not in d2

    def test_06_object_load_and_dump_with_extra_fields_enabled(self):
        d = {
            "make": "Mitsubishi",
            "model": "Lancer",
            "year": 2005,
            "nickname": "Lancer Evo",
        }

        c = Car._load(d)

        assert hasattr(c, "make")
        assert hasattr(c, "model")
        assert hasattr(c, "year")
        assert hasattr(c, "nickname")

        self.assert_all_in(["make", "model", "year", "nickname"], c._dump())

    def test_07_collection_mixin(self):
        class ResultMixin(CollectionBase):
            _key = String()
            _timestamp = DateTime()
            stats = String()

        class PingResult(ResultMixin, Collection):
            __collection__ = "ping_results"
            host = String(required=True)
            status = String(required=True)  # UP, DOWN, SLOW
            error_message = String()
            stats = Dict()

        self.assert_all_in(
            ["_key", "_timestamp", "host", "status", "error_message", "stats"],
            PingResult._fields,
        )

        assert (
                type(PingResult._fields["stats"]) is Dict
        )  # not String from ResultMixin

    def test_08_multi_level_collection_inheritence(self):
        class ResultMixin(CollectionBase):
            _key = String()
            _timestamp = DateTime()
            stats = String()

        class Result(ResultMixin):
            host = String(required=True)
            status = String(required=True)  # UP, DOWN, SLOW
            error_message = String()

        class PingResult(Result, Collection):
            __collection__ = "ping_results"

            stats = Dict()

        print(PingResult._fields.keys())
        self.assert_all_in(
            ["_key", "_timestamp", "host", "status", "error_message", "stats"],
            PingResult._fields,
        )

        assert (
                type(PingResult._fields["stats"]) is Dict
        )  # not String from ResultMixin

    def test_09_load_from_instance_with_extra_patch_data(self):
        p = Person(
            name="test", _key="12312", dob=date(year=2016, month=9, day=12)
        )
        np = Person._load({"name": "Wonder"}, instance=p)

        assert p.name == "test"
        assert np.name == "Wonder"
        assert np._key == "12312"

    def test_10_dirty_fields(self):
        p1 = Person(
            name="test", _key="12312", dob=date(year=2016, month=9, day=12)
        )
        p2 = Person._load(
            {
                "_key": "37405-4564665-7",
                "dob": "2016-09-12",
                "name": "Kashif Iftikhar",
            }
        )
        self.assert_has_same_items(
            p1._dirty, ["name", "_key", "dob", "age", "is_staff", "hobby", "favorite_hobby"]
        )
        self.assert_has_same_items(
            p2._dirty, ["name", "_key", "dob", "age", "is_staff", "hobby", "favorite_hobby"]
        )

        p1._dirty.clear()
        p1.name = "test"  # change name, even if the same as before!
        self.assert_has_same_items(p1._dirty, ["name"])

    def test_11_key_field(self):
        class Person(Collection):
            __collection__ = "persons"
            _key_field = "name"

            name = String(required=True, allow_none=False)
            age = Integer(allow_none=True, missing=None)

        p1 = Person(_key="abc", age=30)
        assert p1._key == "abc"
        assert p1._key == p1.name
        assert p1.age == 30

        p2 = Person()
        p2.name = "xyz"
        assert p2._key == p2.name

        p3 = Person(name="JL")
        assert p3._key == p3.name

    def test_12_nested_field(self):
        pd = {
            "_key": "37405-4564665-7",
            "dob": "2016-09-12",
            "name": "Kashif Iftikhar",
            "favorite_hobby":
                {
                    "name": "Programming",
                    "type": "Challenging"
                }
        }
        new_person = Person._load(pd)
        self.assertEqual("37405-4564665-7", new_person._key)
        self.assertEqual("Kashif Iftikhar", new_person.name)
        self.assertEqual(date(year=2016, month=9, day=12), new_person.dob)
        self.assertEqual("37405-4564665-7", new_person._key)
        self.assertEqual("Programming", new_person.favorite_hobby.name)
        self.assertEqual("Challenging", new_person.favorite_hobby.type)

    def test_13_nested_list_field(self):
        pd = {
            "_key": "37405-4564665-7",
            "dob": "2016-09-12",
            "name": "Kashif Iftikhar",
            "hobby": [
                {
                    "name": "Skydiving",
                    "type": "Extreme",
                    "equipment": [{
                        "name": "parachute",
                        "price": 2000.00
                    }],
                },
                {
                    "name": "Knitting",
                    "type": "Relaxing"
                },

            ]
        }
        
        new_person = Person._load(pd)
        self.assertEqual("37405-4564665-7", new_person._key)
        self.assertEqual("Kashif Iftikhar", new_person.name)
        self.assertEqual(date(year=2016, month=9, day=12), new_person.dob)
        self.assertEqual("37405-4564665-7", new_person._key)

        self.assertEqual(2, len(new_person.hobby))
        skydiving = new_person.hobby[0]
        self.assertEqual(skydiving.name, "Skydiving")
        self.assertEqual(skydiving.type, "Extreme")
        self.assertEqual(len(skydiving.equipment), 1)
        self.assertEqual(skydiving.equipment[0].name, "parachute")
        self.assertEqual(skydiving.equipment[0].price, 2000.00)

        knitting = new_person.hobby[1]
        self.assertEqual(knitting.name, "Knitting")
        self.assertEqual(knitting.type, "Relaxing")
