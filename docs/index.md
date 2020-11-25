<p align="center">
  <a href="https://www.entitykb.org">
    <img src="https://www.entitykb.org/img/logo.png" alt="EntityKB">
  </a>
  <br/>
  <em>
    EntityKB is a Python toolkit for the rapid development of custom
    knowledge bases.
  </em>
</p>

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

EntityKB is a toolkit for creating knowledge bases (i.e. knowledge graphs)
using the Python programming language.


### Use Cases

EntityKB could provide useful capabilities for a wide variety of use cases.
Below are some examples:

* **Entity Extraction**: Identify entities in text using keyword and
  grammar-based pattern matching.
  
* **Entity Linking**: Use graph relationships to provide context for
  typeahead/autocomplete, semantic search, recommendations, or chatbots.

* **Object Storing**: Store and retrieve data for rapid application development
  without SQL calls or object-relational mapping.

* **Data Set Labeling**: Use entity extraction to generate labeled data
  using keywords and grammars to bootstrap training sets.


### Capabilities

EntityKB provides a focused set of core capabilities that can be
extended and enhanced:

* **Graph-based data model** for storing of entities (nodes) and their
  relationships (edges).
  
* **Terms index** for efficient storing and retrieval of entity names and
  synonyms.
  
* **Processing pipeline** that normalizes and tokenizes text and then
  resolves entities from spans of tokens.

* **Searching** with fluent, pythonic traversal query builder for walking
 and filtering graph nodes and relationships.

* **Importing and exporting** of data with CLI tooling and/or Python code.
  
* **Multiple interfaces** including embedded Python client, RPC/HTTP servers
  and CLI.
  
* **Key-value store** for adding and retrieving Python objects in local
  memory or over RPC/HTTP calls.


  
### Priorities

The goal of EntityKB is to make it "easy" to create custom knowledge
bases where "easy" is defined as "**fast to start**" and "**simple
to change**".  The below [quality
attributes](https://en.wikipedia.org/wiki/List_of_system_quality_attributes)
have been prioritized in service to this overarching goal:

* **Efficiency**: Immediately start adding entities and processing text
  with default setup.

* **Configurability**: Add custom code and replace default code by editing a
  simple JSON file.
  
* **Interoperability**: Interact via command-line, RPC, HTTP, or in-memory
  Python library.

* **Relevancy**: Create new entity classes, contextual labels/verbs,
  and custom resolvers with domain specific grammars.

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
  
* **Not memory optimized**: EntityKB is not a "big data" solution.
  The default graph store trades memory for runtime performance and
  ease-of-use. However, the default storage component could be replaced
  with a new one that offloads data to disk or a new graph component
  that delegates to a scalable backend like Neo4j.

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
index.db

$ cat ~/.entitykb/config.json
{
    "graph": "entitykb.InMemoryGraph",
    "modules": [],
    "normalizer": "entitykb.LatinLowercaseNormalizer",
    "searcher": "entitykb.DefaultSearcher",
    "storage": "entitykb.PickleStorage",
    "terms": "entitykb.TrieTermsIndex",
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
+------------------------------------+-------------------------------------+
| config.graph                       |              entitykb.InMemoryGraph |
| config.modules                     |                                  [] |
| config.normalizer                  |   entitykb.LatinLowercaseNormalizer |
| config.pipelines.default.extractor |           entitykb.DefaultExtractor |
| config.pipelines.default.filterers |                                  [] |
| config.pipelines.default.resolvers |           ['entitykb.TermResolver'] |
| config.root                        |          /Users/ianmaurer/.entitykb |
| config.searcher                    |            entitykb.DefaultSearcher |
| config.storage                     |              entitykb.PickleStorage |
| config.terms                       |             entitykb.TrieTermsIndex |
| config.tokenizer                   |        entitykb.WhitespaceTokenizer |
| entitykb.version                   |                             20.12.0 |
| graph.edges                        |                                   0 |
| graph.nodes                        |                                   0 |
| storage.disk_space                 |                             84.00 B |
| storage.last_commit                |                                     |
| storage.path                       | /Users/ianmaurer/.entitykb/index.db |
| terms.links_count                  |                                   0 |
| terms.longest_word                 |                                   0 |
| terms.nodes_count                  |                                   0 |
| terms.sizeof_node                  |                                  32 |
| terms.total_size                   |                                   0 |
| terms.words_count                  |                                   0 |
+------------------------------------+-------------------------------------+
```

### Interact

Start a new Knowledge Base and add two entities:

```python
>>> from entitykb import KB, Entity
>>> kb = KB()
>>> kb.save_node(Entity(name="New York", label="STATE"))
Entity(key='New York|STATE', label='STATE', data=None, name='New York', synonyms=())
>>> kb.save_node(Entity(name="New York City", label="CITY", synonyms=["NYC"]))
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',))
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

Commit the KB to disk, otherwise the saved nodes will be lost on exit.
```python
>>> kb.commit()
True
```

Dump and load the data for safe transfer to a different version of EntityKB:
```bash
$ entitykb dump /tmp/out.jsonl
$ wc -l /tmp/out.jsonl
2
$ entitykb clear
Are you sure you want to clear: /Users/ianmaurer/.entitykb/index.db? [y/N]: y
INFO:     Clear completed successfully.
$ entitykb load /tmp/out.jsonl
Loaded 2 in 0.01s [/tmp/out.jsonl, jsonl]
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

* [pyahocorasick](https://github.com/WojciechMula/pyahocorasick)
  is used for storing strings and retrieving terms from text.
  
* [Typer](https://github.com/tiangolo/typer) powers EntityKB's
  Command Line Interface (CLI) tool.

* [FastAPI](https://github.com/tiangolo/fastapi) powers EntityKB's
  HTTP Application Programming Interface (API).

* [uvicorn](https://github.com/encode/uvicorn) and
  [Starlette](https://github.com/encode/starlette) for power running FastAPI.
  
* [Pydantic](https://github.com/samuelcolvin/pydantic/) for model
  annotations, schema definition and FastAPI documentation.
  
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
