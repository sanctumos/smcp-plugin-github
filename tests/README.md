# Test Suite Documentation

This directory contains a comprehensive test suite for the SMCP GitHub & Git Plugins with 100% code coverage.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (mocked dependencies)
│   ├── test_gh_plugin.py
│   └── test_git_plugin.py
├── integration/            # Integration tests (real CLI tools)
│   ├── test_gh_integration.py
│   └── test_git_integration.py
└── e2e/                     # End-to-end tests (full workflows)
    ├── test_gh_e2e.py
    └── test_git_e2e.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests use mocked subprocess calls to test individual functions in isolation. These tests:
- Don't require external CLI tools (`gh`/`git`)
- Run quickly
- Test all code paths including error conditions
- Cover edge cases and boundary conditions

**Coverage:**
- `run()` function: all argument combinations, dry-run mode, success/failure/timeout/exception cases
- `describe()` function: structure and content validation
- `main()` function: CLI argument parsing, error handling, all command paths

### Integration Tests (`tests/integration/`)

Integration tests use real CLI tools to verify the plugins work correctly with actual commands. These tests:
- Require `gh` CLI (for gh plugin tests)
- Require `git` CLI (for git plugin tests)
- Test real command execution
- Verify output parsing and error handling

**Markers:**
- `@pytest.mark.integration`
- `@pytest.mark.requires_gh` (for gh plugin tests)
- `@pytest.mark.requires_git` (for git plugin tests)

### End-to-End Tests (`tests/e2e/`)

E2E tests verify complete workflows from CLI entry point to output. These tests:
- Test the full CLI interface
- Verify JSON output format
- Test error propagation
- Validate complete user workflows

**Markers:**
- `@pytest.mark.e2e`
- `@pytest.mark.requires_gh` (for gh plugin tests)
- `@pytest.mark.requires_git` (for git plugin tests)

## Running Tests

### Run All Unit Tests (Recommended for CI)

```bash
pytest tests/ -m unit -v
```

### Run Integration Tests

```bash
# Requires gh/git CLI installed
pytest tests/ -m integration -v
```

### Run E2E Tests

```bash
# Requires gh/git CLI installed
pytest tests/ -m e2e -v
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=plugins --cov-report=html --cov-report=term-missing
```

## Coverage Requirements

The test suite is configured to require **100% code coverage**. This is enforced by:
- `--cov-fail-under=100` in pytest configuration
- Coverage reports in HTML, XML, and terminal formats
- Branch coverage enabled

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- `mock_subprocess_run`: Mocks subprocess.run for unit tests
- `mock_subprocess_timeout`: Mocks timeout exceptions
- `mock_subprocess_exception`: Mocks generic exceptions
- `check_command_available`: Helper to check if CLI tools are available

## Adding New Tests

When adding new functionality:

1. **Add unit tests first** - Test the function in isolation with mocks
2. **Add integration tests** - Test with real CLI tools if applicable
3. **Add E2E tests** - Test complete workflows
4. **Verify coverage** - Ensure new code is covered by tests
5. **Run all tests** - Verify nothing breaks

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    ...

@pytest.mark.integration
@pytest.mark.requires_git
def test_with_git():
    ...
```

## Continuous Integration

The test suite is designed to run in CI environments:

- Unit tests run without external dependencies
- Integration/E2E tests are skipped if CLI tools aren't available
- Coverage reports are generated for analysis
- Tests fail if coverage drops below 100%

