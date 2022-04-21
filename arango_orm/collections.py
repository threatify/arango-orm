"""
Collections Module
------------------

Core classes for working with collections (vertices) and relations (edges).
"""

import logging
import typing
from marshmallow.fields import String
from six import with_metaclass
from marshmallow import (
    Schema,
    fields,
    ValidationError,
    missing,
    EXCLUDE,
    INCLUDE,
    post_load)

from .references import (
    Relationship,
    GraphRelationship,
)  # pylint: disable=E0402
from .exceptions import (  # pylint: disable=E0402
    MemberExistsException,
    DetachedInstanceError,
    SerializationError,
)

log = logging.getLogger(__name__)


class CollectionMeta(type):
    def __new__(mcs, name, bases, attrs):

        super_new = super(CollectionMeta, mcs).__new__

        new_fields = {}
        refs = {}

        for obj_name, obj in attrs.items():

            if isinstance(obj, fields.Field):
                # add to schema fields
                new_fields[obj_name] = attrs.get(obj_name)

            elif isinstance(obj, (Relationship, GraphRelationship)):
                refs[obj_name] = attrs.get(obj_name)

        for k in new_fields:
            attrs.pop(k)

        new_class = super_new(mcs, name, bases, attrs)
        new_class._fields = dict(
            getattr(new_class, "_fields", {}), **new_fields
        )
        new_class._refs = refs

        return new_class


class ObjectSchema(Schema):
    object_class: callable = None
    @post_load
    def make_object(self, data, **kwargs):
        return self.object_class(**data)

    def __del__(self):
        '''Help GC cleanup'''
        self.fields = None
        self.load_fields = None
        self.dump_fields = None

class CollectionBase(with_metaclass(CollectionMeta)):
    "Base class for Collections, Nodes and Links"

    _key_field = None
    _allow_extra_fields = False
    _collection_config = {}

    _inheritance_field = None
    _inheritance_mapping = {}

    @classmethod
    def get_objects_dict(cls):
        objects_dict = cls._fields.copy()

        if cls.__name__ != CollectionBase().__class__.__name__:
            for c in cls.__bases__:
                if issubclass(c,CollectionBase):
                    base_objects_dict = c.get_objects_dict()
                    for i, f in [(i, f) for i, f in base_objects_dict.items() if i not in objects_dict]:
                        objects_dict[i] = f

        return objects_dict

    @classmethod
    def schema(cls,only:typing.List[str]=None):
        '''schema caches Marshmellow Schemas on this class to preserve memory'''
        if not hasattr(cls,'_cls_schema'):
            objects_dict = cls.get_objects_dict()
            cls._cls_schema = type(
                cls.__name__ + "Schema", (ObjectSchema,), objects_dict
            )
        
        # Extra fields related schema configuration
        unknown = EXCLUDE
        if cls._allow_extra_fields is True:
            unknown = INCLUDE            

        if not hasattr(cls,'_cls_schema_cache'):
            #print(f'making {cls.__name__} schema with only=None')
            SC = cls._cls_schema()
            SC.unknown = unknown
            SC.object_class = cls
            cls._cls_schema_cache = {None:SC}

        if only is not None:
            #create a unique schema for this input by using a hashable set
            if isinstance(only,(list,tuple)): 
                onlyKey = str(set(only)) #garuntees order / uniquness and hashability
            else:
                onlyKey = only 

            if onlyKey not in cls._cls_schema_cache:
                SC = cls._cls_schema(only=only)
                SC.unknown = unknown
                SC.object_class = cls
                cls._cls_schema_cache[onlyKey] = SC #asssign the unique schema for only
            
            return cls._cls_schema_cache[onlyKey] #return the unique schema with onlykey
        
        else:
            return cls._cls_schema_cache[None]


class Collection(CollectionBase):
    """Base class for representing collections (or vertices as called in AranogDB)."""

    __collection__ = None

    _safe_list = [
        "__collection__",
        "_safe_list",
        "_relations",
        "_id",
        "_index",
        "_collection_config",
        "_post_process",
        "_pre_process",
        "_fields_info",
        "_fields",
        "_db",
        "_refs",
        "_refs_vals",
    ]

    def __init__(self, collection_name=None, **kwargs):
        if collection_name is not None:
            self.__collection__ = collection_name

        self._dirty = set()
        self._refs_vals = (
            {}
        )  # initialize container for relationship and graph_relationship values

        # cls._Schema().load(in_dict)
        if "_key" not in kwargs:
            self._key = None

        for field_name, field in self._fields.items():  # pylint: disable=E1101
            default_value = None if field.default is missing else field.default
            if callable(default_value):
                default_value = default_value()
            setattr(self, field_name, kwargs.pop(field_name, default_value))

        # FIXME: shall we ignore attrs not defined in schema
        for k, v in kwargs.items():
            setattr(self, k, v)

        if self._inheritance_field is not None \
                and getattr(self, self._inheritance_field) is None \
                and self.__class__.__name__ in self._inheritance_mapping:
            setattr(self, self._inheritance_field, self._inheritance_mapping[self.__class__.__name__])

    def __setattr__(self, attr, value):
        a_real = attr
        if attr == self._key_field:
            a_real = "_key"
        if attr == "_id":
            return
        super(Collection, self).__setattr__(a_real, value)

        if a_real not in self._fields:
            return

        self._dirty.add(a_real)

    def __str__(self):
        ret = "<" + self.__class__.__name__

        if hasattr(self, "_key"):
            ret += "(_key=" + str(getattr(self, "_key")) + ")"

        ret += ">"

        return ret

    def __repr__(self):
        return self.__str__()

    def __del__(self):
        '''Removes references between schema and fields to help GC cleanup '''
        for parm,field in self._fields.items(): #Clear Fields
            if hasattr(field,'parent'): field.parent = None
            if hasattr(field,'root'): field.root  = None

        old_dirt = self._dirty
        self._dirty = None #Clear Dirt Set References
        del old_dirt

        oldf = self._fields
        self._fields = tuple()
        del oldf

    def __getattribute__(self, item):

        # print("__getatttribute__ called!")
        if item not in super(Collection, self).__getattribute__("_refs"):
            key_field = super(Collection, self).__getattribute__("_key_field")
            if item == key_field:
                return super(Collection, self).__getattribute__("_key")
            else:
                return super(Collection, self).__getattribute__(item)

        if item not in super(Collection, self).__getattribute__("_refs_vals"):
            # print("trying to load ref val")
            # pdb.set_trace()
            if (
                hasattr(self, "_db") is False
                or super(Collection, self).__getattribute__("_db") is None
            ):  # pylint: disable=E1101
                raise DetachedInstanceError()

            db = super(Collection, self).__getattribute__(
                "_db"
            )  # pylint: disable=E1101
            ref_class = super(Collection, self).__getattribute__("_refs")[
                item
            ]  # pylint: disable=E1101

            r_val = None
            if "_key" == ref_class.target_field:
                r_val = db.query(ref_class.col_class).by_key(
                    super(Collection, self).__getattribute__(ref_class.field)
                )  # pylint: disable=E1101

                if ref_class.uselist is True:
                    r_val = [
                        r_val,
                    ]

            else:
                if ref_class.uselist is False:
                    r_val = (
                        db.query(ref_class.col_class)
                        .filter(
                            ref_class.target_field + "==@val",
                            val=super(Collection, self).__getattribute__(
                                ref_class.field
                            ),  # pylint: disable=E1101
                        )
                        .first()
                    )

                else:
                    # TODO: Handle ref_class.order_by if present
                    r_val = (
                        db.query(ref_class.col_class)
                        .filter(
                            ref_class.target_field + "==@val",
                            val=super(Collection, self).__getattribute__(
                                ref_class.field
                            ),  # pylint: disable=E1101
                        )
                        .all()
                    )

            if ref_class.cache is True:
                super(Collection, self).__getattribute__("_refs_vals")[
                    item
                ] = r_val  # pylint: disable=E1101
            else:
                return r_val

        return super(Collection, self).__getattribute__("_refs_vals")[
            item
        ]  # pylint: disable=E1101

    @classmethod
    def _load(cls, in_dict, only=None, instance=None, db=None):
        "Create object from given dict."
        if instance:
            in_dict = dict(instance._dump(), **in_dict)

        # save the instance's creation schema,
        # so we can dump the instance with the orginal schema
        schema = cls.schema(only=only)

        extra_fields = INCLUDE
        if cls._allow_extra_fields is False:
            extra_fields = EXCLUDE

        data = schema.load(in_dict, unknown=extra_fields)

        # add any extra fields present in in_dict into data
        # if cls._allow_extra_fields:
        #     for k, v in in_dict.items():
        #         if k not in data and not k.startswith("_"):
        #             data[k] = v

        new_obj = data
        new_obj._instance_schema = schema

        if db:
            new_obj._db = db
        else:
            new_obj._db = getattr(instance, "_db", None)

        if hasattr(new_obj, "_pre_process"):
            new_obj._pre_process()

        if "_key" in in_dict and (
            not hasattr(new_obj, "_key") or new_obj._key is None
        ):
            setattr(new_obj, "_key", in_dict["_key"])

        if "_id" in in_dict:
            new_obj.__collection__ = in_dict["_id"].split("/")[0]

        if hasattr(new_obj, "_post_process"):
            new_obj._post_process()

        if db is not None:
            # no dirty fields if initializing an object from db
            new_obj._dirty.clear()

        return new_obj

    # def validate(self):
    #     """Validate data."""
    #     return self.schema().validate(self._dump())

    def _dump(self, only=None, **kwargs):
        """Dump all object attributes into a dict."""
        schema = None

        if hasattr(self, "_instance_schema"):
            schema = self._instance_schema

        if only is not None:
            schema = self.schema(only=only)

        if schema is None:
            schema = self.schema()

        data = schema.dump(self)

        # if errors:
        #     raise SerializationError(
        #         "Error dumping object of collection {} - {}".format(
        #             self.__class__.__name__, errors
        #         )
        #     )

        if "_key" not in data and hasattr(self, "_key"):
            data["_key"] = getattr(self, "_key")

        if "_key" in data and data["_key"] is None:
            del data["_key"]

        # Also dump extra fields as is without any validation or conversion
        if self._allow_extra_fields:
            for prop in dir(self):
                if hasattr(self.__class__, prop) and isinstance(
                    getattr(self.__class__, prop),
                    (property, Relationship, GraphRelationship),
                ):

                    continue

                if (
                    prop in data
                    or callable(getattr(self, prop))
                    or prop.startswith("_")
                ):
                    continue

                data[prop] = getattr(self, prop)

        validation_errors = schema.validate(data)

        if validation_errors:
            raise ValidationError(validation_errors)

        return data

    @property
    def _id(self):
        if hasattr(self, "_key") and getattr(self, "_key") is not None:
            return self.__collection__ + "/" + getattr(self, "_key")

        return None


class Relation(Collection):

    _safe_list = [
        "__collection__",
        "_safe_list",
        "_id",
        "_collections_from",
        "_collections_to",
        "_object_from",
        "_object_to",
        "_index",
        "_collection_config",
        "_fields",
        "_db",
        "_refs",
        "_refs_vals",
    ]

    def __init__(self, collection_name=None, **kwargs):

        self._dirty = set()

        if "_collections_from" in kwargs:
            self._collections_from = kwargs["_collections_from"]
        else:
            self._collections_from = None

        if "_collections_to" in kwargs:
            self._collections_to = kwargs["_collections_to"]
        else:
            self._collections_to = None

        self._from = None
        self._to = None
        self._object_from = None
        self._object_to = None

        super(Relation, self).__init__(
            collection_name=collection_name, **kwargs
        )

    def __str__(self):
        ret = "<" + self.__class__.__name__ + "("

        if hasattr(self, "_key"):
            ret += "_key=" + str(getattr(self, "_key"))

        if hasattr(self, "_from") and hasattr(self, "_to"):
            ret += ", _from={}, _to={}".format(
                str(getattr(self, "_from", "")), str(getattr(self, "_to"))
            )

        ret += ")>"

        return ret

    @classmethod
    def _load(cls, in_dict, only=None, instance=None, db=None):
        "Create object from given dict"

        if instance:
            in_dict = dict(instance._dump(), **in_dict)

        schema = cls.schema(only=only)

        extra_fields = INCLUDE
        if cls._allow_extra_fields is False:
            extra_fields = EXCLUDE

        data = schema.load(in_dict, unknown=extra_fields)
        # remove _id field
        # if "_id" in data:
        #     del data["_id"]

        new_obj = data
        new_obj._instance_schema = schema

        if db:
            new_obj._db = db
        else:
            new_obj._db = getattr(instance, "_db", None)

        if hasattr(new_obj, "_pre_process"):
            new_obj._pre_process()

        if "_key" in in_dict and (
            not hasattr(new_obj, "_key") or new_obj._key is None
        ):
            setattr(new_obj, "_key", in_dict["_key"])

        if "_id" in in_dict:
            new_obj.__collection__ = in_dict["_id"].split("/")[0]

        if "_from" in in_dict:
            setattr(new_obj, "_from", in_dict["_from"])

        if "_to" in in_dict:
            setattr(new_obj, "_to", in_dict["_to"])

        if hasattr(new_obj, "_post_process"):
            new_obj._post_process()

        if db is not None:
            # no dirty fields if initializing an object from db
            new_obj._dirty.clear()

        return new_obj

    def _dump(self, only=None, **kwargs):
        """Dump all object attributes into a dict."""
        data = super(Relation, self)._dump(only=only, **kwargs)

        if "_from" not in data and hasattr(self, "_from"):
            data["_from"] = getattr(self, "_from")

        if "_to" not in data and hasattr(self, "_to"):
            data["_to"] = getattr(self, "_to")

        return data
