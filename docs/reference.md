## Code Inventory

This [sortable table](https://squidfunk.github.io/mkdocs-material/reference/data-tables/#sortable-tables)
provides an inventory of important classes, modules, and functions.

| Module                | Item                      | Description                                               | 
| --------------------- | ---------------           | --------------------------------------------------------- | 
| cli                   | commands.py               | Functions that are available via command line.            |
| cli                   | readers.py                | Default file readers for CSV and JSONL file types.        |
| contrib.date          | date.lark                 | [Lark](https://github.com/lark-parser/lark) grammar.      | 
| contrib.date          | Date                      | Example entity with fields for year, month, day.          |
| contrib.date          | DateResolver              | Example resolver for finding Date entities.               |
| contrib.email         | Email                     | Example entity with fields for username and domain.       |
| contrib.email         | EmailResolver             | Example resolver that finds email entities.               |
| deps                  | Environ                   | Env vars that prevents setting previously read values.    |
| graph                 | Graph                     | Abstract class for graph reading and writing.             |
| graph                 | InMemoryGraph             | Default graph that keeps data in memory using indices.    |
| graph                 | NodeIndex                 | Stores nodes by their key and label for fast retrieval.   |
| graph                 | EdgeIndex                 | Stores edges for retrieval by verb, direction or node.    |
| http                  | admin                     | [Svelte](https://svelte.dev/)-based admin web UI.         |
| http                  | app                       | [FastAPI](https://fastapi.tiangolo.com/)-based HTTP API.  |
| http                  | dev                       | Startup and shutdown parallel RPC with hot reloading.     |
| http                  | prod                      | Default startup and shutdown functions.                   |
| http                  | routes                    | API declarations with delegation to RPC KB server.        |
| kb                    | KB                        | Embeddable, in-memory KB with core functions.             |
| models.doc            | Doc                       | Created by pipeline, contains text, spans, and tokens.    |
| models.doc            | Span                      | Span is a set of tokens and a resolved entity.            |
| models.doc            | DocToken                  | Token plus it's offset within the Doc.                    |
| models.doc            | Token                     | String of the token with helper functions for detokenize. |
| models.entity         | Entity                    | Node with name, synonyms and key ("`name|LABEL`").        |
| models.enums          | Direction                 | Traversal and index flag for incoming or outcoming.       |
| models.enums          | Comparison                | Criteria flag for search filtering (i.e. less than).      |
| models.node           | Node                      | Base class for objects (key, label, data) stored in graph.|
| models.node           | Edge                      | Base class for relationships (verb) between nodes.        |
| models.registry       | Registry                  | Creates nodes and edges from dict based on label/verb.    |
| models.registry       | Schema                    | Pydantic schema of nodes by labels and edges by verbs.    |
| models.registry       | Lookup                    | Mapping of labels to Node type and verbs to Edge types.   |
| models.search         | SearchRequest             | Container for search starts, traversal, limit, and offset.| 
| models.search         | SearchResponse            | Container for nodes and trails returned from search.      |
| models.search         | Trail                     | Search path from start node through a series of hops.     |
| models.search         | Hop                       | Search step from start to end node via 1 or more edges.   |
| models.traverse       | Verb                      | String with operator overrides for creating edge criteria.|
| models.traverse       | F                         | Helper class with operator override for field criteria.   |
| models.traverse       | T                         | Short-cut for Traversal class.                            |
| models.traverse       | Traversal                 | Collector of traversal steps with walk and filter helpers.|
| models.traverse       | WalkStep                  | Instruct searcher to hop via edges to neighboring nodes.  |
| models.traverse       | FilterStep                | Filter searching based on criteria with all/exclude flags.|
| models.traverse       | EdgeCriteria              | Filtering criteria based on edges and neighboring nodes.  |
| models.traverse       | FieldCriteria             | Filtering criteria based on node field value.             |
| pipeline.extractor    | Extractor                 | Base-class for extracting document from text.             |
| pipeline.extractor    | DefaultExtractor          | Creates handlers, processes tokens, and collects spans.   |
| pipeline.filterer     | Filterer                  | Base class for filtering spans.                           |
| pipeline.filterer     | ExactNameOnly             | Only keep spans that exactly match to the entity name.    |
| pipeline.filterer     | KeepLongestByKey          | Keeps longest overlapping span with same node key.        |
| pipeline.filterer     | KeepLongestByLabel        | Keeps longest overlapping span with same node label.      |
| pipeline.filterer     | KeepLongestByOffset       | Keeps longest overlapping span using token offsets.       |
| pipeline.filterer     | LowerNameOrExactSynonym   | Keeps when lower name or exact synonym match.             |
| pipeline.handler      | TokenHandler              | Manages resolver prefix tokens state during extraction.   |
| pipeline.normalizers  | Normalizer                | Base class for normalizing text.                          |
| pipeline.normalizers  | LatinLowercaseNormalizer  | Default normalizer that converts text to lowercase ASCII. |
| pipeline.pipeline     | Pipeline                  | Container of resolvers and filterers, does extract/filter.|
| pipeline.resolvers    | Resolver                  | Base class with is_prefix and resolve methods.            |
| pipeline.resolvers    | TermResolver              | Resolves entities from terms using TrieTermsIndex.        |
| pipeline.tokenizers   | Tokenizer                 | Base class with tokenize and detokenize methods.          |
| pipeline.tokenizers   | WhitespaceTokenizer       | Default tokenizer that splits on whitespace characters.   |
| rpc.client_async      | AsyncKB                   | Remote KB client that supports async/await calls.         |
| rpc.client_sync       | SyncKB                    | Remote KB client that supports synchronous calls.         |
| rpc.connection        | RPCConnection             | Connection manager used by KB clients and RPC server.     |
| rpc.server            | RPCServer                 | Asyncio socket server that handles RPC calls.             |
| rpc.server            | HandlerKB                 | Used by RPCServer to delegate calls to in-memory KB.      |
| searcher              | Searcher                  | Base class Searcher uses starts and steps to yield trails.|
| searcher              | DefaultSearcher           | Naive first implementation that uses layered generators.  |
| searcher              | StartLayer                | Generator layer that yields trail objects from start keys.|
| searcher              | WalkLayer                 | Layer that recursively walks graph using walk steps.      |
| searcher              | FilterLayer               | Layer that filters trails based on edge or field criteria.|
| storage               | Storage                   | Base class for saving and loading KB data.                |
| storage               | PickleStorage             | Default storage class that uses pickle (de)serialization. |
| terms                 | TermsIndex                | Base class for storing/retrieving entity terms.           |
| terms                 | TrieTermsIndex            | Default terms index built using [pyahocorasick](https://pyahocorasick.readthedocs.io/en/latest/).|
| config                | Config                    | Handles reading and writing of KB configuration files.    |
| config                | PipelineConfig            | Describes configuration of each named pipeline in KB.     |
| env                   | Environ                   | Default environment values with getter/setter properties. |


## Class Diagram

This [mermaid diagram](https://mermaid-js.github.io/mermaid/#/classDiagram)
shows the major components of EntityKB and how they interrelate. See other
sections for better viewing of specific subsections or try zooming.

```mermaid
 classDiagram

    class KB {
        get_node(key)
        save_node(node)
        remove_node(key)

        save_edge(edge)

        parse(request)
        search(request)

        commit()
        clear()
        reload()
        info()
    }

    KB "1" --> "1" Config: config

    class Config {
        graph: str
        modules: List[str]
        normalizer: str
        searcher: str
        storage: str
        terms: str
        tokenizer: str
    }

    KB "1" --> "1" Storage: storage

    class Storage {
        root: str = None
        max_backups: int = 5
        load()
        save()
        archive()
        info()
    }

    KB "1" --> "1" TermsIndex: terms

    class TermsIndex {
        add_entity(entity)
        remove_entity(entity)

        add_term(key, term)
        remove_term(key, term)

        is_prefix(prefix): bool
    }

    KB "1" --> "*" Pipeline: pipelines

    class Pipeline {
        __call__(text, labels)
    }

    Pipeline "1" --> "1" Extractor: extractor

    class Extractor {
        __call__(text, labels)
    }

    Extractor "1" --> "*" TokenHandler: handlers

    class TokenHandler {
        __call__(text, labels)
    }


    Token Handler "1" --> "1" Resolver: resolvers
    Extractor "1" --> "*" Resolver: resolvers

    class Resolver {
        is_prefix(term)
        resolve(term)
    }

    Resolver <|-- TermResolver: is a

    class TermResolver {
    }

    TermResolver ..> TermsIndex: calls

    TermsIndex "1" --> "1" Normalizer: normalizer
    Resolver "1" --> "1" Normalizer: normalizer

    class Normalizer {
        normalize(text)
    }

    Normalizer <|-- LatinLowercaseNormalizer: is a

    class LatinLowercaseNormalizer {
    }

    Extractor "1" --> "1" Tokenizer: tokenizer
    Resolver "1" --> "1" Tokenizer: tokenizer

    class Tokenizer {
        tokenize(text)
        detokenize(tokens)
    }

    Tokenizer <| -- WhitespaceTokenizer: is a

    class WhitespaceTokenizer {
    }

    Pipeline "1" --> "*" Filterer: filterers

    class Filterer {
        filter(spans, tokens)
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

    Pipeline ..> Doc: generates

    class Doc {
        text: str
        entities(): Tuple[Entity]
    }

    Doc "1" --> "*" DocToken : tokens

    class DocToken {
        offset: str
    }

    DocToken "1" --> "1" Token: token

    class Token {
        __root__: str
        ws_after: bool
        left_token: Token
        __add__(other): Token
    }

    Doc "1" --> "*" Span : spans

    class Span {
        entity_key: str
    }

    Span "1" --> "*" DocToken : tokens
    Span "1" --> "1" Entity : entity

    class Searcher {
        starts: Iterable
        initialize()
    }

    Searcher ..> Graph: searches
    Searcher --> Layer: layer

    class Layer {
    }

    Layer <|-- StartLayer

    class StartLayer {
        starts: Iterable
    }

    Layer <|-- WalkLayer

    class WalkLayer {
        step: WalkStep
        prev: Layer
        seen: Set
    }

    Layer <|-- FilterLayer

    class FilterLayer {
        step: FilterStep
        prev: Layer
    }

    class SearchRequest {
        q: str
        labels: List[str]
        keys: List[str]
        limit: int = 100
        offset: int = 0
    }

    SearchRequest "1" --> "1" Traversal: traversal

    class Traversal {
        
    }

    Traversal "1" --> "*" Step: steps

    class Step {
    }

    Step <|-- WalkStep

    class WalkStep {
        verbs: List[str]
        directions: List[Direction]
        max_hops: int = 1
        passthru: bool = False
    }

    Step <|-- FilterStep

    class FilterStep {
        all: bool = False
        exclude: bool = False
    }

    FilterStep "1" --> "*" Criteria: criteria

    class Criteria {
    }

    Criteria <|-- FieldCriteria

    class FieldCriteria {
        field: str
        compare: Comparison
        value: Any
        type: str = "field"
    }

    Criteria <|-- EdgeCriteria

    class EdgeCriteria {
        verbs: List[str]
        directions: List[Direction]
        keys: List[str]
        type: str = "edge"
    }

    class SearchResponse {
        nodes: List[Node]
    }

    SearchResponse "1" --> "*" Trail: trails

    class Trail {
        start: str
        copy(): Trail
        push(end, edge): Trail
    }

    Trail "1" --> "*" Hop: hops

    class Hop {
        start: str
        end: str
        edges: List[Edge]
    }
```
