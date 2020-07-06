<img src='./docs/images/entitykb-logo.png' width='140' alt="EntityKB Logo"/>

`EntityKB` is a Python library, that supports “rules-based” Named Entity
Recognition (NER) and Entity Linking.

EntityKB can be thought of as a reverse search engine. With a typical
search engine, such as Solr or Elasticsearch, a corpus of documents
is loaded into the system and queries, composed of a single keyword
or phrase, when executed against the store return a set of matching
documents sorted by relevancy. With EntityKB, a corpus of entities
are loaded or programmed into system and queries, composed of the
complete text of a document, when executed return a set of matching
entities sorted by token position.

This technology can be used for a wide variety of Information
Extraction (IE) use-cases including unstructured medical record
abstraction, web scraping keyword identification, voice/chat-bot
knowledge base, data normalization/de-duping and ML training data
set bootstrapping.

Documentation coming soon, below is a quick how-to guide to get started.

## Getting Started


EntityKB can be installed from the Python Package Index (PyPI) using pip:

```
$ pip install entitykb
```

The Command Line Interface (CLI) should now be available on your terminal:

```
$ entitykb
Usage: entitykb [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  info     Print entitykb stats and meta information.
  init     Initialize new entitykb root directory.
  load     Load data from CSV/TSV input file or stream.
  process  Process text into a document (JSON) or entity rows.
  reset    Reset an entitykb index.
```

### EntityKB Root Directory

EntityKB works from a configuration and data file based in a root
directory. To initialize this root directory, you would use the
`entitykb init` command.

One option is to use the default path `~/.entitykb`:

```
$ entitykb init
Creating KB directory: /Users/ianmaurer/.entitykb
Initializing KB: /Users/ianmaurer/.entitykb
Initialization Complete.
```

Another option is to use the environment variable `ENTITYKB_ROOT` such as:

```
$ export ENTITYKB_ROOT=/tmp/demo
$ entitykb init
Creating KB directory: /tmp/demo
Initializing KB: /tmp/demo
Initialization Complete.
```

The final option is pass the root directory along to every command
as an option (`--root_dir`) but that is not recommended.

Once your directory is created, you should see the following files
and configuration JSON:

```bash
$ ls
config.json	index.db

$ cat config.json
{
 "extractor": "entitykb.DefaultExtractor",
 "filterers": [

 ],
 "index": "entitykb.DefaultIndex",
 "normalizer": "entitykb.DefaultNormalizer",
 "resolvers": [
  "entitykb.DefaultResolver"
 ],
 "tokenizer": "entitykb.DefaultTokenizer"
}
```

### Entity Indexing

Entity data can be loaded from Comma (CSV) or Tabbed-Separated
Values (TSV) files using the CLI tool. Below is an example CSV file
where multiple synonyms are split by the default separator (pipe
`|`):

```bash
$ cat entities.csv
name,synonyms,label
New York City,NYC|New York (NY),CITY
New York,NY,STATE
United States,USA|US,COUNTRY
```

Performing a load “dry-run” makes this information a little easier to read:

```
$ entitykb load entities.csv --dry-run
+---------------+---------+--------------------------+
| name          | label   | synonyms                 |
+---------------+---------+--------------------------+
| New York City | CITY    | ('NYC', 'New York (NY)') |
| New York      | STATE   | ('NY',)                  |
| United States | COUNTRY | ('US', 'USA')            |
+---------------+---------+--------------------------+
Dry run complete. Loaded 0 records.
```

Loading this document, by removing the `--dry-run` option, creates 3 entities and 8 terms for the 3 names and 5 synonyms.

```bash
$ entitykb load entities.csv
Loaded 3 records.
```

You can view the information about your knowledge base using the `info` command:

```
$ entitykb info
+--------------------+----------------------------+
| config.extractor   |  entitykb.DefaultExtractor |
| config.filterers   |                            |
| config.index       |      entitykb.DefaultIndex |
| config.normalizer  | entitykb.DefaultNormalizer |
| config.resolvers   |   entitykb.DefaultResolver |
| config.tokenizer   |  entitykb.DefaultTokenizer |
| config.path        |      /tmp/demo/config.json |
| index.nodes_count  |                         82 |
| index.words_count  |                         12 |
| index.longest_word |                         22 |
| index.links_count  |                         81 |
| index.sizeof_node  |                         32 |
| index.total_size   |                       3272 |
| index.entity_count |                          3 |
| index.path         |         /tmp/demo/index.db |
| index.disk_space   |                  1007.00 B |
| index.in_memory    |                   3.30 KiB |
| index.last_commit  | 2020-06-30 08:58:45.074304 |
| load_time          |                0.00061 sec |
| is_dirty           |                      False |
+--------------------+----------------------------+
```

### Document Processing

Given the first sentence from Wikipedia about New York City:

```bash
$ cat example.txt
New York City (NYC), often called New York (NY),
is the post populous city in the United States.

```

We can then extract indexed entities using the `process` command:

```
$ entitykb process example.txt
+---------------+-------------------+-----------------------+
| text          | tokens            | key                   |
+---------------+-------------------+-----------------------+
| New York City | 0, 1, 2           | New York City|CITY    |
| New York      | 0, 1              | New York|STATE        |
| NYC           | 4                 | New York City|CITY    |
| New York (NY) | 9, 10, 11, 12, 13 | New York City|CITY    |
| New York      | 9, 10             | New York|STATE        |
| NY            | 12                | New York|STATE        |
| United States | 22, 23            | United States|COUNTRY |
+---------------+-------------------+-----------------------+
```

This above tabular format is for viewing purposes, you can also
generate the full document as JSON or each entity as a JSONL record
using the following options:

```bash
$ entitykb process --json example.txt
$ entitykb process --jsonl example.txt
```

Notice that there are overlapping entities. The first 2 tokens
(0=New, 1=York) is both part of the 3 token CITY and 2 token STATE.
The default behavior is to return all entities for downstream
processing. The EntityKB library comes with some built in Filterers
including `KeepLongestOnly` which will suppress any overlapping
entities by keeping the longest one regardless of label.

You can add it to the `config.json` file like this:

```
{
 ...

  "filterers": [
    "entitykb.KeepLongestOnly"
  ],

 ...
}

```

And then when run again, notice all of the STATE label New York
entities are removed:

```
$ entitykb process example.txt
+---------------+-------------------+-----------------------+
| text          | tokens            | key                   |
+---------------+-------------------+-----------------------+
| New York City | 0, 1, 2           | New York City|CITY    |
| NYC           | 4                 | New York City|CITY    |
| New York (NY) | 9, 10, 11, 12, 13 | New York City|CITY    |
| United States | 22, 23            | United States|COUNTRY |
+---------------+-------------------+-----------------------+
```

### Python Processing
 
To process documents using EntityKB Python library, you need to
create a `KB` object using the `entitykb.load` method using either
an explicit root path (passed in as a string) or relying on the
`ENTITYKB_ROOT` environment variable. If no path is specified, then
EntityKB will fall back to the default user root path (`~/.entitykb/`).

```
$ export ENTITYKB_ROOT=/tmp/demo
$ python

>>> import entitykb
>>> kb = entitykb.load()
>>> kb.info()
{ 
  ...
  'entity_count': 3,
  'path': '/tmp/demo/index.db',
  ...
}
```

With a `KB` object you can now use it to process text and generate
a `Doc` object:

```
>>> doc = kb("In New York you can be a new man")
>>> type(doc)
entitykb.model.Doc
>>> doc.text
'In New York you can be a new man'
```

Off of the doc, you can access the tokens:
```
>>> doc.tokens
(In [offset: 0],
 New [offset: 1],
 York [offset: 2],
 you [offset: 3],
 can [offset: 4],
 be [offset: 5],
 a [offset: 6],
 new [offset: 7],
 man [offset: 8])
```

You can also access the entities, their tokens and the entity:
```
>>> doc.entities
(New York,)
>>> doc.entities[0].tokens
(New [offset: 1], York [offset: 2])
>>> doc.entities[0].entity
New York|STATE
```

The entity has a name, key, label, synonyms and any meta information loaded:
```
>>> doc.entities[0].entity.dict()
{'name': 'New York',
 'key': 'New York|STATE',
 'label': 'STATE',
 'synonyms': ('NY',),
 'meta': None}
```

