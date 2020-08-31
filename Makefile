SHELL := /bin/bash

rpc:
	PIPENV_IGNORE_VIRTUALENVS=1 PYTHONPATH=src pipenv run entitykb rpc

http:
	PIPENV_IGNORE_VIRTUALENVS=1 PYTHONPATH=src pipenv run entitykb http

ipython:
	PIPENV_IGNORE_VIRTUALENVS=1 PYTHONPATH=src pipenv run ipython

test:
	PIPENV_IGNORE_VIRTUALENVS=1 PYTHONPATH=src pipenv run pytest -c pytest.ini

coverage:
	PIPENV_IGNORE_VIRTUALENVS=1 PYTHONPATH=src pipenv run pytest -c pytest-coverage.ini

white:
	white src/ tests/

update:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv update --dev
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv lock -r --dev > dev-requirements.txt

tox: clean
	tox

# clean

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	find . -name 'htmlcov' -exec rm -fr {} +
	find . -name '.coverage' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.cache' -exec rm -fr {} +
	find . -name '.mypy_cache' -exec rm -fr {} +
	find . -name '.tox' -exec rm -fr {} +

# publish

publish:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel --universal
	pipenv run twine upload -r pypi dist/*