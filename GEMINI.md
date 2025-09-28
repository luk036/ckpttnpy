# Gemini Code Assistant Context

## Project Overview

This project, `ckpttnpy`, is a Python library for circuit partitioning. It provides tools for partitioning hypergraphs into multiple parts while maintaining balance and optimization criteria. The core of the library is a multi-level partitioning algorithm that iteratively refines an initial partition to improve its quality.

The library is well-structured, following modern Python packaging practices. It uses `setuptools` for packaging, `pytest` for testing, and `tox` for automation. The code is formatted with `black` and linted with `flake8`, ensuring a high level of code quality and consistency.

## Building and Running

### Dependencies

The project has the following dependencies:

- `networkx`: For graph data structures and algorithms.
- `luk036/mywheel`: A custom wheel.
- `luk036/netlistx`: A library for handling netlists.

### Installation

To set up a development environment, run the following commands:

```bash
pip3 install git+https://github.com/luk036/mywheel.git
pip3 install git+https://github.com/luk036/netlistx.git
pip3 install -r ./requirements.txt &&
python3 setup.py develop
```

### Running Tests

To run the unit tests, use the following command:

```bash
python3 setup.py test
```

or

```bash
tox
```

## Development Conventions

### Code Style

The project uses `black` for code formatting and `isort` for sorting imports. `flake8` is used for linting. These checks are enforced using pre-commit hooks.

### Testing

The project uses `pytest` for unit testing. The tests are located in the `tests` directory and cover a variety of scenarios, including randomly generated hypergraphs and hypergraphs read from JSON files.

### Documentation

The project uses `Sphinx` to generate documentation. The documentation is located in the `docs` directory and is written in reStructuredText and Markdown. The API documentation is automatically generated from the source code using `sphinx-apidoc`.

To build the documentation, run the following command:

```bash
tox -e docs
```

### Contribution Guidelines

The `CONTRIBUTING.md` file provides a template for contribution guidelines. While it has not been fully filled out, it indicates that the project follows a standard fork and pull request workflow.
