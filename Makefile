.PHONY: all clean doc lint test test3 test2 dist pypi pypi_test coverage

PYTHON2 := python2.7
PYTHON3 := python3.3

all:
	false

clean:
	rm -rf build dist ezstruct/*.pyc tests/*.pyc \
	  $$(find . -name \*~) \
	  $$(find . -name \*.pyc) \
	  ezstruct/__pycache__ \
	  ezstruct.egg-info \
	  doc/_build \
	  .coverage \
	  coverage.out/*

doc:
	cd doc && sphinx-build -a -b html . ./_build

lint:
	pylint --rcfile=pylint.cfg ezstruct
	check-manifest

test: test3 test2

test2:
	PYTHONPATH=. $(PYTHON2) tests/test_ezstruct.py

test3:
	PYTHONPATH=. $(PYTHON3) tests/test_ezstruct.py

dist:
	$(PYTHON3) setup.py sdist
	$(PYTHON3) setup.py bdist_wheel

pypi: clean dist
	twine upload -r pypi dist/*

pypi_test: clean dist
	twine upload -r test dist/*

coverage:
	PYTHONPATH=. python3 -m coverage run --branch --source=ezstruct tests/test_ezstruct.py
	PYTHONPATH=. $(PYTHON3) -m coverage html -d coverage.out
