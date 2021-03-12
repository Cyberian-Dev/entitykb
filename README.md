<h1>💡 EntityKB</h1>

Python toolkit for the rapid development of custom knowledge bases.

---

**EntityKB Documentation**:
<a href="https://www.entitykb.org" target="_blank">
    https://www.entitykb.org
</a>

**EntityKB Code Repository**:
<a href="https://github.com/genomoncology/entitykb" target="_blank">
    https://github.com/genomoncology/entitykb
</a>

**EntityKB Python Package**:
<a href="https://pypi.org/project/entitykb/" target="_blank">
    https://pypi.org/project/entitykb/
</a>

---

## Overview

EntityKB is a toolkit for rapidly developing knowledge bases (i.e.
[knowledge graphs](https://en.wikipedia.org/wiki/Knowledge_Graph))
using the Python programming language. It combines an text processing
pipeline with a graph data store to support rules/string-based
entity extraction and linking.


### Potential Use Cases

* **Entity Extraction**: Pull concepts from unstructured text using using
  keyword and pattern matching.
  
* **Entity Linking**: Map concepts to a knowledge graph for "semantic 
  searching" capabilities for recommendation systems, Q&A, data
  harmonization, and validated data entry (i.e. drop downs, typeahead).

* **Data Set Labeling**: Overcome the "cold start" training set problem
  by using entity extraction capabilities to generate annotations.

* **Knowledge Curation/Integration**: Iteratively add new data types 
  and sources with simple Python model classes and data loaders.

### Capabilities

EntityKB provides a focused set of core capabilities that can be
extended and enhanced:

* **Graph data store** for storing of entities (nodes) and their
  relationships (edges) as plain-old python objects.
  
* **Terms and Edge index** for efficient retrieval and traversal of
  entities using their name, synonyms, and relationships.
  
* **Processing pipeline** that normalizes and tokenizes text and then
  resolves entities using string, regex, grammar or python based matching.

* **Searching** with fluent, pythonic traversal query builder for walking
 and filtering graph nodes and their relationships.

* **Importing and exporting** of data with CLI tooling and/or Python code.
  
* **Multiple interfaces** including embedded Python client, RPC/HTTP servers
  and CLI.
  
### Priorities

EntityKB's core goal is to enable the rapid, iterative development of custom
knowledge graphs using Python. The following
[quality attributes](https://en.wikipedia.org/wiki/List_of_system_quality_attributes)
have been prioritized in furtherance of this goal:

* **Evolvability**: Add, update and remove entity types and
  data sources without time-consuming data migrations.

* **Configurability**: Activate and deactivate out-of-the-box components and
  custom code by editing a simple JSON file.
  
* **Interoperability**: Interact via command-line, RPC, HTTP, or in-memory
  Python library based on evolving project needs.

* **Understandability**: Create new entity classes, contextual labels/verbs,
  and custom resolvers with domain specific language and concepts.

* **Portability**: Code and data created for EntityKB should be
  transferable to a new technology stack with minimal effort.
  
  
### Limitations

EntityKB is deliberately limited in scope to minimize complexity.
Below are some choices that users should be aware of upfront:

* **Not secure**: EntityKB has no authentication or authorization
  capabilities. RPC and HTTP services should not be exposed to
  untrusted clients. Instead, proxy EntityKB behind your application's
  security layer. Also, knowledge bases are stored using pickles
  which are not secure, only unpickle data from trusted sources.
  
* **Python-based**: The most critical data structures are powered by
  libraries written in the C programming language for high-performance
  and tight memory management. However, this library is still mostly
  Python-based and will certainly not meet everyone's runtime needs.

* **Not transactional**: EntityKB is not designed for ACID-compliant
  data storage and should never be used as the "system of record". 
  EntityKB can be updated during runtime, but care should be taken to
  prevent data loss or corruption.
  
* **Not ML based**: EntityKB is a software development platform
  without any out-of-the-box machine learning capabilities. However, it
  certainly can be used in larger ML-based projects and custom resolvers
  can be added that use ML models for their entity detection logic.
  
* **Not Resilient**: EntityKB graph searching capability has no
  guards against long-running queries that can impact system
  responsiveness. Limit end user's from creating open-ended queries to
  prevent service disruption.
  
---
  
## Getting Started

### Install

```bash
$ pip install entitykb
```

### Initialize

EntityKB `init` creates a KB in the specified "root" directory. The root
directory is determined using the following priorities:

1. Command-line argument
2. Environment variable (ENTITYKB_ROOT)
3. Default path (~/.entitykb)

Below are the `init` and `info` commands using the default path. Notice
the default configuration specifies implementation classes that can be
overridden using the `config.json` file. The `index.db` contains the graph
and terms index data in python pickle format and can be deployed with the
config.json to any server using the same version of EntityKB.

```text
$ entitykb init
INFO:     Initialization completed successfully.

$ ls ~/.entitykb/
config.json
edges
edges.dawg
nodes
nodes.dawg

$ cat ~/.entitykb/config.json
{
    "graph": "entitykb.Graph",
    "modules": [],
    "normalizer": "entitykb.LatinLowercaseNormalizer",
    "searcher": "entitykb.DefaultSearcher",
    "terms": "entitykb.TermsIndex",
    "tokenizer": "entitykb.WhitespaceTokenizer",
    "pipelines": {
        "default": {
            "extractor": "entitykb.DefaultExtractor",
            "resolvers": [
                "entitykb.TermResolver"
            ],
            "filterers": []
        }
    }
}

$ entitykb info
+------------------------------------+-----------------------------------+
| config.graph                       |                    entitykb.Graph |
| config.modules                     |                                   |
| config.normalizer                  | entitykb.LatinLowercaseNormalizer |
| config.pipelines.default.extractor |         entitykb.DefaultExtractor |
| config.pipelines.default.filterers |                                   |
| config.pipelines.default.resolvers |             entitykb.TermResolver |
| config.root                        |        /Users/ianmaurer/.entitykb |
| config.searcher                    |          entitykb.DefaultSearcher |
| config.terms                       |               entitykb.TermsIndex |
| config.tokenizer                   |      entitykb.WhitespaceTokenizer |
| entitykb.version                   |                          20.12.14 |
| graph.edges                        |                                 0 |
| graph.nodes                        |                                 0 |
+------------------------------------+-----------------------------------+
```

### Interact

Start a new Knowledge Base and add two entities:

```python
>>> from entitykb import KB, Entity
>>> kb = KB()

>>> nys = Entity(name="New York", label="STATE")
>>> kb.save_node(nys)

>>> nyc = Entity(name="New York City", label="CITY", synonyms=["NYC"])
>>> kb.save_node(nyc)
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',))
```

Edge objects can be created using the Edge class or the right/left-shift
methods on nodes. The `Verb` (or short-hand `V`) can be used or so can
a simple string. The library converts all verbs to uppercase:

```python
>>> from entitykb import Edge, Verb, V 

>>> Edge(start="New York City|CITY", verb=V.IS_IN, end=nys)
Edge(start='New York City|CITY', verb='IS_IN', end='New York|STATE')

>>> nyc >> Verb.IS_IN >> nys
Edge(start='New York City|CITY', verb='IS_IN', end='New York|STATE')

>>> nys << V.is_in << nyc
Edge(start='New York City|CITY', verb='IS_IN', end='New York|STATE')

>>> nys << "is_in" << "New York City|CITY"
Edge(start='New York City|CITY', verb='IS_IN', end='New York|STATE')
```

Edges still need to be saved to the graph which can be accomplished using
the `save_edge` or `connect` methods:

```python
>>> edge = nyc >> Verb.IS_IN >> nys
>>> kb.save_edge(edge)

>>> kb.connect(start=nyc, verb="IS_IN", end=nyc)
Edge(start='New York|STATE', verb='IS_IN', end='New York City|CITY')
```

To index the terms and edges of the Graph store, you must first run the 
`reindex` method on the KB:

```python
>>> kb.reindex()
```

Perform term search using common prefix text:
```python
>>> response = kb.search("New Y")
>>> len(response)
2
>>> response[0]
Entity(key='New York|STATE', label='STATE', data=None, name='New York', synonyms=())
>>> response[1]
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',))
```

Parse text into a document with tokens and spans containing entities:
```python
>>> doc = kb.parse("NYC is another name for New York City")
>>> len(doc.tokens)
8
>>> doc.spans
(NYC, New York City)
>>> doc.entities
(Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',)),
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',)))
```

The dump command generates JSONL:
```bash
$ entitykb dump
{"kind": "node", "payload": {"key": "New York|STATE", "label": "STATE", "data": null, "name": "New York", "synonyms": []}}
{"kind": "node", "payload": {"key": "New York City|CITY", "label": "CITY", "data": null, "name": "New York City", "synonyms": ["NYC"]}}
{"kind": "edge", "payload": {"__root__": ["New York City|CITY", "IS_IN", "New York|STATE"]}}
```


Dump and load the data for safe transfer to a different version of EntityKB:
```bash
$ entitykb dump /tmp/out.jsonl
$ wc -l /tmp/out.jsonl
2
$ entitykb clear
Are you sure you want to clear: /Users/ianmaurer/.entitykb/index.db? [y/N]: y
INFO:     Clear completed successfully.

$ # do version switch here.

$ $ entitykb load /tmp/out.jsonl
Loaded 2 in 0.02s [/tmp/out.jsonl, jsonl]
Reindexed in 0.01s
```

---

## Background

### History

EntityKB was developed by [GenomOncology](https://www.genomoncology.com/)
and is the foundation of the clinical, molecular and genomic knowledge
base that power GenomOncology's [igniteIQ data extraction
platform](https://genomoncology.com/igniteiq) and [clinical decision
support API suite](https://genomoncology.com/api-suite). EntityKB
was released as an open source library in November 2020 for the
benefit of GenomOncology's clients and the greater open source
community.


### Maintainer

The initial version of EntityKB was designed and implemented by Ian Maurer
who is the Chief Technology Officer (CTO) for GenomOncology. Ian has over
20 years of industry experience and is the architect of GenomOncology's 
[igniteIQ data extract platform](https://genomoncology.com/igniteiq) and
[API Suite](https://genomoncology.com/api-suite) that powers GenomOncology's
[Precision Oncology Platform](https://www.genomoncology.com/our-platform).

Ian can be contacted via [Twitter](https://twitter.com/imaurer),
[LinkedIn](https://www.linkedin.com/in/ianmaurer/), or email
(ian -at- genomoncology.com).


### Related Projects

EntityKB was inspired by and is powered by several other projects in the
open source community. Below are the most salient examples:

* [DAWG](https://dawg.readthedocs.io/en/latest/)
  is used for indexing edge relationships (triples), terms, and labels. It
  supports "completion" of terms based on a prefix.
  
* [DiskCache](http://www.grantjenks.com/docs/diskcache/)
  is used for storing nodes and edges to disk as python objects.
  
* [Pydantic](https://github.com/samuelcolvin/pydantic/) for model
  annotations, schema definition and FastAPI documentation.
  
* [Typer](https://github.com/tiangolo/typer) powers EntityKB's
  Command Line Interface (CLI) tool.

* [FastAPI](https://github.com/tiangolo/fastapi) powers EntityKB's
  HTTP Application Programming Interface (API).

* [uvicorn](https://github.com/encode/uvicorn) and
  [Starlette](https://github.com/encode/starlette) for power running FastAPI.
  
* [MkDocs](https://github.com/mkdocs/mkdocs/), 
  [Termynal.js](https://github.com/ines/termynal/), and
  [Material for MkDocs](https://github.com/squidfunk/mkdocs-material)
  for making the documentation look great.
  
* [Lark](https://github.com/lark-parser/lark) for powering the date
  resolver's grammar.
  
* [FlashText](https://github.com/vi3k6i5/flashtext) for inspiring
  parts of EntityKB's design and approach.


### License

This project is copyrighted by [GenomOncology](https://www.genomoncology.com/)
and licensed under the terms of the MIT license.

---

## Status

EntityKB should be considered beta software. Some caveats:

* Expect backwards incompatible changes that will break your Knowledge Base.
  When that happens, run the following steps:
       1. Using the old version of EntityKB, run the `dump` CLI command to
          generate a JSONL file of your edges and nodes.
       2. Switch to the new version of EntityKB, and run the `load` CLI command
          to import the edges and nodes from JSONL.

* Monitor changes in the [release notes](release-notes.md).

* To minimize frustration, please pin the version of the software in
  your requirements.txt or equivalent file.
 
---
  
## Contributing

* Submit bugs and enhancement suggestions via
  [GitHub issues](https://github.com/genomoncology/entitykb/issues).
  
* Contributions welcome, please see [Development](development.md) for
  setting up a working dev environment.
  
* Our goal is to keep EntityKB's code footprint as small as possible
  but `contrib` modules will be more readily accepted.
  
* Separate packages don't require a pull request, but please follow the
  naming pattern `entitykb-<name>` to aid in discoverability on pypi.
