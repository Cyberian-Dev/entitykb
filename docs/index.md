<p align="center">
  <a href="https://www.entitykb.org">
    <img src="https://www.entitykb.org/img/logo.png" alt="EntityKB">
  </a>
  <br/>
  <em>
    EntityKB is a python toolkit for the rapid development of custom
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

---

# Background

EntityKB is a toolkit for quickly creating knowledge bases (a.k.a.
knowledge graphs) using the python programming language.  Knowledge
bases enable [entity linking](https://en.wikipedia.org/wiki/Entity_linking)
for information extraction and structured searching projects.
For example, web scraping scripts or chat bot applications can provide
greater value when concepts are linked to a traversable semantic graph.

EntityKB was developed by [GenomOncology](https://www.genomoncology.com/)
and is the foundation of the clinical, molecular and genomic knowledge
base that power GenomOncology's [igniteIQ data extraction
platform](https://genomoncology.com/igniteiq) and [clinical decision
support API suite](https://genomoncology.com/api-suite). EntityKB
was released as an open source library (MIT License) in November
2020 for the benefit of GenomOncology's clients and the greater
open source community.

Out of the box, EntityKB is a programmatic framework for algorithmic text
mining techniques, not a machine-learning based NLP solution. However, 
EntityKB could be used in conjunction with NLP and other deep learning
tools for real-world solutions.


### Capabilities

EntityKB provides a focused set of core capabilities that can be built upon:

* **Graph-based data model** for storing of entities (nodes) and their
  relationships (edges).
  
* **Terms index** for efficient storing and retrieval of entity names and
  synonyms.
  
* **Processing pipeline** that normalizes, tokenizes and extracts entities
  from text.

* **Searching** with python based query and traversal language.

* **Importing and exporting** of data with CLI tooling and/or Python code.
  
* **Multiple interfaces** including embedded Python client, RPC/HTTP servers
  and CLI.

  
### Priorities

The goal of EntityKB is to make it "easy" to create custom Knowledge Bases.
Where "easy" is defined as "**Fast to Start**" and "Simple to Change".
The below priorities are in service to this overarching goal:

* **Up and Running**: Immediately start adding entities and processing
  text with the default KB configuration.

* **Configurable**: Add custom or replace default code by editing a simple
  JSON file.
  
* **Multiple Interfaces**: Embed as Python library, manage via CLI,
  or invoke remotely via RPC or HTTP.

* **Domain Specific**: Create new entity types using type annotated
  [Pydantic](https://pydantic-docs.helpmanual.io/) models and custom
  resolvers using grammars or other Domain Specific Language (DSL)
  programming techniques.

* **Portable**: Code and data created for EntityKB should be easy to
  transfer to a new framework or approach.
  

### Limitations

EntityKB is deliberately limited in scope to minimize complexity.
Below are some choices that users should be aware of before starting:

* **Not secure**: EntityKB has no authentication or authorization
  capabilities. RPC and HTTP services should not be exposed to
  untrusted clients. Instead, proxy EntityKB behind your application's
  security layer.
  
* **Heavy RAM usage**: EntityKB is not a "big data" solution.
  The default graph store trades RAM for runtime performance and ease-of-use.
  However, the storage could be replaced with a new implementation
  via configuration.

* **Not transactional**: EntityKB is not designed for ACID-compliant
  data storage and should never be used as the "System of Record". 
  EntityKB can be updated during runtime, but care should be taken to
  prevent data loss or corruption.
  
* **No Machine Learning**: EntityKB is a software development platform
  without any out-of-the-box machine learning capabilities. However, it
  certainly can be used in larger ML-based projects and custom resolvers
  can be added that have "ML models" at their heart of the code.
  
# Getting Started

### Install

```bash
$ pip install entitykb
```

### Initialize

EntityKB creates a KB in the path specified by the ENTITYKB_ROOT environment
variable. If no variable is provided, then the user's ~/.entitykb path is
used.

```text
$ entitykb init
INFO:     Initialization completed successfully.

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
| entitykb.version                   |                               0.9.0 |
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

```
>>> from entitykb import KB, Entity
>>> kb = KB()
>>> kb.save_node(Entity(name="New York", label="STATE"))
Entity(key='New York|STATE', label='STATE', data=None, name='New York', synonyms=())
>>> kb.save_node(Entity(name="New York City", label="CITY", synonyms=["NYC"]))
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',))
```

Perform term search using common prefix text:
```
>>> response = kb.search("New Y")
>>> len(response)
2
>>> response[0]
Entity(key='New York|STATE', label='STATE', data=None, name='New York', synonyms=())
>>> response[1]
Entity(key='New York City|CITY', label='CITY', data=None, name='New York City', synonyms=('NYC',))
```

Parse text into a document with tokens and spans containing entities:
```
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
```
>>> kb.commit()
True
```


## License

This project is copyrighted by
[GenomOncology](https://www.genomoncology.com/) and licensed under
the terms of the MIT license.
