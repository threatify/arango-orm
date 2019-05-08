# Quick Recipes For Common Tasks

## Make \_key for collection auto-increment

```python
class MyCollection(Collection):

    __collection__ = 'my_collection'
    _collection_config = {
        'key_generator': 'autoincrement'
    }

    _key = String(required=True)
    title = String(required=True)
```


## Index on additional fields

```python
class IPAddress(Collection):
    """IP address collection."""

    __collection__ = 'ip_addresses'
    _index = [
        {"type": "geo", "fields": ["geo_location"]}
    ]

    _key = String(required=True)  # the actual ip address
    ip_version = Integer(required=True, options=[4, 6])
    description = String(default='')
    geo_location = List(Float)
```
