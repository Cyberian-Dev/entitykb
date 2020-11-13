## Developing

If you already cloned the repository and you know that you need to deep dive
in the code, here are some guidelines to set up your environment.

### Using Pipenv

Below are the steps using [Pipenv](https://pipenv.pypa.io/en/latest/) and
Makefiles to setup and test your environment:

<div class="termy">
```console
$ make update
$ make test
$ make coverage
```
</div>

### Using Virtualenv

Below are steps using Python's virtualenv module to setup and test your
environment:

<div class="termy">
```console
$ python -m venv venv
$ source ./venv/bin/activate
(venv) $ pip install -r dev-requirements.txt 
(venv) $ pytest -c pytest.ini
(venv) $ pytest -c pytest-coverage.ini
```
</div>


### Format

There is a script that you can run that will format and clean all your code:

<div class="termy">

```console
$ make white
```

</div>

## Docs

The documentation uses <a href="https://www.mkdocs.org/" class="external-link" target="_blank">MkDocs</a>.

All the documentation is in Markdown format in the directory `./docs`.

Many of the tutorials have blocks of code.

In most of the cases, these blocks of code are actual complete applications
that can be run as is.

In fact, those blocks of code are not written inside the Markdown, they are
Python files in the `./docs_src/` directory.

And those Python files are included/injected in the documentation when
generating the site.

### Live Docs

Most of the tests actually run against the example source files in the
documentation.

This helps making sure that:

* The documentation is up to date.
* The documentation examples can be run as is.
* Most of the features are covered by the documentation, ensured by test coverage.

During local development, there is a script that builds the site and checks
for any changes, live-reloading:

<div class="termy">

```console
$ make docs-live

<span style="color: green;">[INFO]</span>    -  Building documentation...
<span style="color: green;">[INFO]</span>    -  Cleaning site directory
<span style="color: green;">[INFO]</span>    -  Documentation built in 2.74 seconds
<span style="color: green;">[INFO]</span>    -  Serving on http://127.0.0.1:8008
```

</div>

It will serve the documentation on `http://127.0.0.1:8008`.

That way, you can edit the documentation/source files and see the changes live.

## Test Coverage

There is a script that you can run locally to test all the code and generate
coverage reports in HTML:

<div class="termy">

```console
$ make coverage
```

</div>

This command generates a directory `./htmlcov/`, if you open the file
`./htmlcov/index.html` in your browser, you can explore interactively the
regions of code that are covered by the tests, and notice if there is any
region missing.