# Agent Guidelines for ckpttnpy

## Build, Lint, and Test Commands

### Running Tests
```bash
# Run all tests
python3 setup.py test
# Or
pytest

# Run a single test
pytest tests/test_FMConstrMgr.py::test_check_legal

# Run with coverage (default)
pytest --cov ckpttnpy --cov-report term-missing

# Run tests via tox (isolated environment)
tox
```

### Linting and Formatting
```bash
# Run flake8 (linting)
flake8 src/ tests/

# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Build
```bash
# Build package in isolation
python -m build .

# Clean build artifacts
python -c 'from shutil import rmtree; rmtree("build", True); rmtree("dist", True)'
```

## Code Style Guidelines

### Project Structure
- Source code: `src/ckpttnpy/`
- Tests: `tests/`
- Package uses namespace packages (configured in setup.cfg)
- Version managed via setuptools_scm

### Naming Conventions
- **Classes**: CamelCase (e.g., `FMConstrMgr`, `PartMgrBase`, `LegalCheck`)
- **Functions/Methods**: snake_case (e.g., `check_legal`, `update_move`)
- **Variables**: lowercase_with_underscores or short lowercase names
- **Constants**: UPPER_CASE (e.g., `LegalCheck.NotSatisfied`)
- **Private methods**: Prefix with underscore (e.g., `_optimize_1pass`)

### Type Hints
- Required on all function signatures
- Use `typing` module for complex types
- Common patterns:
  ```python
  from typing import Any, Dict, Generic, Iterable, List, TypeVar, Union

  Part = Union[Dict[Any, int], List[int]]
  Gnl = TypeVar("Gnl", bound=Iterable[int])
  ```

### Docstrings
- Use Google-style or PEP 257 docstrings
- Include `Args:` and `Returns:` sections
- Provide usage examples where appropriate
- Include detailed module-level docstrings explaining algorithmic logic
- Example:
  ```python
  def check_legal(self, move_info_v):
      """Check if a move is legal under balance constraints.

      Args:
          move_info_v: Tuple of (vertex, from_part, to_part)

      Returns:
          LegalCheck: NotSatisfied, GetBetter, or AllSatisfied
      """
  ```

### Code Organization
- Use abstract base classes with `@abstractmethod` for interfaces
- Use Enums for status codes and constants
- Use `__slots__` for classes to reduce memory usage
- Include module-level metadata (`__author__`, `__copyright__`, `__license__`)

### Error Handling
- Use `assert` for invariants and preconditions
- Return status codes (e.g., `LegalCheck` enum) rather than raising for algorithmic states
- Test error conditions with `pytest.raises`

### Python Version
- Minimum: Python 3.8 (conditional imports for version compatibility)
- Use modern typing features when available

### Import Order
- Standard library imports first
- Third-party imports second
- Local imports third (from `.module import ...`)

### Configuration Files
- `setup.cfg`: Package metadata, pytest options, flake8 config
- `pyproject.toml`: Build system configuration (setuptools_scm)
- `.flake8`: Linting rules (extends setup.cfg, Black-compatible)
- `.pre-commit-config.yaml`: Pre-commit hooks (black, isort, flake8)

### Testing Patterns
- Use pytest fixtures for test setup
- Mock external dependencies with simple classes
- Test public interfaces, not private methods
- Use type hints on test functions: `def test_something() -> None:`
