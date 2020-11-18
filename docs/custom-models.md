Custom node and edge classes can be added to your Knowledge Base
by inheriting from `Node` and `Edge` classes. For instance, the
GeoKB has a City class:

```python
from entitykb.models import Entity

class City(Entity):
    latitude: float
    longitude: float
    population: int
    timezone: str
    elevation: int = None
```

By default, custom nodes get a upper, camel case label based on the class.
Such as CUSTOM_NODE for the class CustomNode. You can also provide overrides
to these 2 class level attributes:

```python
class CustomNode(Node):
    __all_labels__ = {"ANOTHER_LABEL"}
    __default_label__ = "DEFAULT_LABEL"
```



### Client-Server

EntityKB uses dict objects to transmit nodes and edges between client and
server. The `Registry` class is responsible for constructing the right
class on both sides when storing or retrieving data. It uses the node "labels"
and the edge "verbs" for mapping.

To ensure proper object construction, both sides need access to the
common class types. The configuration file has a "modules" setting value:

```json
{
     "modules": ["geokb"]
}
```

The Config imports these modules prior to the `Registry` being populated
with all known subclasses of `Node` and `Edge` mapped by their labels
and verbs.

```python
class Config(BaseModel):
    ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for m in self.modules:
            import_module(m)

```

Below is an example for constructing a Node with data dict, where it will
resolve and instantiate the correct class based on the label value:

```python
    node = Node.create(data)
```

