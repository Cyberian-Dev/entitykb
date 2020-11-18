EntityKB stores concepts and their relationships in a graph-based
data structure. Concepts are represented by `Node` python classes and their
relationships are stored as `Edge` classes. An `Entity` is a type of node
with a name and list of synonyms. Nodes have a label and Edges have a verb
along with start and end node keys.

Data should be added and removed via the `KB` interface, not directly through
the `Graph` or it's configured implementation class (i.e. `InMemoryGraph`)
because the KB also adds and removes terms from the `TermsIndex`.

The InMemoryGraph uses `NodeIndex` and `EdgeIndex` to store and retrieve
nodes and edges in a high performance manner.

## Class Diagram

Below is subsection of the full [reference class diagram](reference.md#class-diagram).

```mermaid
 classDiagram

    class KB {
        get_node(key)
        save_node(node)
        remove_node(key)
        save_edge(edge)
        commit()
    }

    KB "1" --> "1" Graph: graph

    class Graph {
        save_node(node: Node)
        get_node(key): Node
        remove_node(key): bool
        save_edge(node: Node)
    }

    Graph "1" --> "*" Node: nodes

    class Node {
        key: str
        label: str
        data: dict = None
        create()$
    }

    Node <|-- Entity: is a

    class Entity {
        name: str
        synonyms: Tuple[str]
        create()$
        terms(): Tuple[str]
    }

    Edge "2" --> "2" Node: subject, domain
    Graph "1" --> "*" Edge: edges

    class Edge {
        start: str
        verb: str
        end: str
        weight: int = 1
        data: dict = None
        create()$
    }


```

