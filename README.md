<p align="center">
  <a href="https://entitykb.org"><img src="./img/logo.png" alt="EntityKB"></a>
</p>
<p align="center">
    <em>EntityKB: Python Knowledge Base Toolset</em>
</p>

---

**Documentation**: <a href="https://www.entitykb.org" target="_blank">https://www.entitykb.org</a>

**Source Code**: <a href="https://github.com/genomoncology/entitykb" target="_blank">https://github.com/genomoncology/entitykb</a>

---

EntityKB is a configurable and extensible toolset for creating custom
Knowledge Bases using the Python programming language.

The key features of EntityKB are:

* **Graph Store**: Store and query nodes/entities and their relationships.
* **Terms Index**: Store and find entities using their names and synonyms.
* **Keyword Extraction**: Tokenize, normalize, extract and filter entities from text.
* **Autocomplete**: Support type-ahead use cases.
* **Load and Dump**: Load data into and export data out of your KB.

There are multiple ways to interact with the Knowledge Base:

* **Python Library**: Import and work with KB directly in your process's memory.
* **Command Line**: Use the entitykb CLI tool for initializing, loading, etc.
* **Remote Procedure Call**: Start RPC server and call it via sync/async SDKs.
* **JSON over HTTP API ("REST-like")**: Start HTTP server and call it via HTTP client.
* **Admin User Interface**: Interact with admin web user interface or Swagger UI.



## Requirements

Python 3.6+

## Installation

<div class="termy">

```console
$ pip install entitykb
---> 100%
Successfully installed entitykb
```

</div>


## License

This project is licensed under the terms of the MIT license.