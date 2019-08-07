# python-mixture

*Mixin classes for great objects !*

[![Python versions](https://img.shields.io/pypi/pyversions/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Build Status](https://travis-ci.org/smarie/python-mixture.svg?branch=master)](https://travis-ci.org/smarie/python-mixture) [![Tests Status](https://smarie.github.io/python-mixture/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mixture/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mixture/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mixture)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-mixture/) [![PyPI](https://img.shields.io/pypi/v/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Downloads](https://pepy.tech/badge/mixture)](https://pepy.tech/project/mixture) [![Downloads per week](https://pepy.tech/badge/mixture/week)](https://pepy.tech/project/mixture) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-mixture.svg)](https://github.com/smarie/python-mixture/stargazers)

**This is the readme for developers.** The documentation for users is available here: [https://smarie.github.io/python-mixture/](https://smarie.github.io/python-mixture/)

## Want to contribute ?

Contributions are welcome ! Simply fork this project on github, commit your contributions, and create pull requests.

Here is a non-exhaustive list of interesting open topics: [https://github.com/smarie/python-mixture/issues](https://github.com/smarie/python-mixture/issues)

## Requirements for builds

Install requirements for setup beforehand using 

```bash
pip install -r ci_tools/requirements-pip.txt
```

## Running the tests

This project uses `pytest`.

```bash
pytest -v mixture/tests/
```


## Packaging

This project uses `setuptools_scm` to synchronise the version number. Therefore the following command should be used for development snapshots as well as official releases: 

```bash
python setup.py egg_info bdist_wheel rotate -m.whl -k3
```

## Generating the documentation page

This project uses `mkdocs` to generate its documentation page. Therefore building a local copy of the doc page may be done using:

```bash
mkdocs build -f docs/mkdocs.yml
```

## Generating the test reports

The following commands generate the html test report and the associated badge. 

```bash
pytest --junitxml=junit.xml -v mixture/tests/
ant -f ci_tools/generate-junit-html.xml
python ci_tools/generate-junit-badge.py
```

### PyPI Releasing memo

This project is now automatically deployed to PyPI when a tag is created. Anyway, for manual deployment we can use:

```bash
twine upload dist/* -r pypitest
twine upload dist/*
```
