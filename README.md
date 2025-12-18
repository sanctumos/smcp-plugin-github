# SMCP GitHub & Git Plugins

[![License: AGPLv3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

SMCP plugins for GitHub CLI (`gh`) and Git command-line tools. These plugins provide MCP-compatible wrappers for interacting with GitHub and Git repositories through the Model Context Protocol.

## Overview

This repository contains two SMCP plugins:

- **gh Plugin**: Wraps the GitHub CLI (`gh`) command for GitHub operations
- **git Plugin**: Wraps the Git command-line tool for repository operations

Both plugins follow the SMCP plugin architecture and can be integrated into any SMCP-compatible MCP server.

## Features

- **MCP Protocol Compliant**: Full compatibility with Model Context Protocol specification
- **SMCP Plugin Format**: Standardized plugin interface for easy integration
- **Error Handling**: Robust error handling with detailed output capture and pattern recognition
- **Idempotency Detection**: Automatically detects and handles idempotent operations (e.g., "already closed", "already exists")
- **Standardized Responses**: Consistent response format with `success` and `error_code` fields for automation
- **Argument Parsing**: Proper handling of multi-word arguments and quoted strings
- **Non-Interactive Mode**: Automatic `--yes` flag injection for non-interactive execution
- **Working Directory Control**: Explicit control over command execution context with `--cwd` flag
- **Dry Run Support**: Test commands without execution
- **Timeout Protection**: Commands timeout after 30 seconds to prevent hanging

## Installation

### Prerequisites

- Python 3.8 or higher
- `gh` CLI tool installed (for gh plugin)
- `git` command-line tool installed (for git plugin)

### Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh
```

**Windows:**
```powershell
winget install GitHub.cli
```

### Install Git

Git is typically pre-installed on most systems. If not:

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install git

# Fedora
sudo dnf install git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/download/win)

## Usage

### Plugin Structure

Each plugin follows the SMCP plugin format:

```
plugins/
├── gh/
│   ├── __init__.py
│   └── cli.py
└── git/
    ├── __init__.py
    └── cli.py
```

### Running Plugins

#### GitHub CLI Plugin

```bash
# Get plugin description
python plugins/gh/cli.py --describe

# Execute a gh command
python plugins/gh/cli.py run --command "repo" --subcommand "list"

# Dry run (see what would be executed)
python plugins/gh/cli.py run --dry-run --command "repo" --subcommand "list"
```

#### Git Plugin

```bash
# Get plugin description
python plugins/git/cli.py --describe

# Execute a git command
python plugins/git/cli.py run --command "status"

# Execute with arguments
python plugins/git/cli.py run --command "log" --args "--oneline" "-10"

# Dry run
python plugins/git/cli.py run --dry-run --command "status"
```

### Integration with SMCP Server

To use these plugins with an SMCP server, place the `plugins` directory in your SMCP server's plugin directory and ensure the server is configured to discover plugins from that location.

Example SMCP server configuration:

```python
# Set environment variable for plugin directory
import os
os.environ["MCP_PLUGINS_DIR"] = "/path/to/smcp-plugin-github/plugins"
```

## Plugin API

### Common Functions

Both plugins implement the standard SMCP plugin interface:

#### `run(args: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]`

Executes the command with the provided arguments.

**Parameters:**
- `args`: Dictionary of command arguments
- `dry_run`: If True, returns what would be executed without running

**Returns:**
- Dictionary with command execution results including:
  - `command`: The executed command string
  - `return_code`: Exit code of the command
  - `elapsed`: Execution time in seconds
  - `stdout`: Standard output
  - `stderr`: Standard error
  - `result`: Combined output (for success) or error message

#### `describe() -> Dict[str, Any]`

Returns the plugin description in SMCP format.

**Returns:**
- Dictionary containing plugin metadata and available commands

## Limitations

This wrapper provides a thin layer over the underlying `gh` and `git` CLI tools. As such, there are some limitations that cannot be addressed at the wrapper level:

### Output Truncation and Large Results

**Issue:** Some commands may have output that is truncated or not properly parsed when results are very large (e.g., long issue lists, large file trees).

**Reason:** Output truncation occurs at the CLI/API level. The wrapper passes through all output from the underlying tools, but if `gh` or `git` truncate output, the wrapper cannot recover the missing data.

**Workaround:** Use pagination flags when available (e.g., `--limit` for `gh` commands) or filter results to reduce output size.

### API Race Conditions and Transient Errors

**Issue:** GitHub API errors (e.g., 502, 422) during operations like repo creation can lead to state mismatches where a repo appears to fail creation but actually exists.

**Reason:** These are API-side race conditions and transient errors that occur at the GitHub API level. The wrapper cannot add atomic "create and confirm" logic without implementing complex retry and state checking logic that would duplicate GitHub CLI functionality.

**Workaround:** The wrapper includes idempotency detection (see Features) which helps handle some "already exists" scenarios. For critical operations, implement retry logic in your automation layer.

### Feature Coverage Limitations

**Issue:** Some GitHub CLI features may not be fully supported or may have limitations (e.g., `--topics` flag behavior, multi-word strings in certain fields).

**Reason:** The wrapper passes commands directly to the underlying `gh` CLI. If a feature is missing or broken in `gh` itself, the wrapper cannot add that functionality.

**Workaround:** Check the [GitHub CLI documentation](https://cli.github.com/manual/) for the latest feature support. Report missing features to the [GitHub CLI project](https://github.com/cli/cli).

### Wrapper Boundaries

The wrapper focuses on:
- ✅ Argument handling and parsing
- ✅ Error message enhancement and context
- ✅ Idempotency detection for common scenarios
- ✅ Working directory and context management
- ✅ Non-interactive flag enforcement
- ✅ Response format standardization

The wrapper cannot:
- ❌ Add features missing from the underlying CLI tools
- ❌ Fix API-level race conditions or transient errors
- ❌ Recover truncated output from CLI/API
- ❌ Implement complex retry logic beyond basic idempotency detection

## Response Format

All plugins return responses in the following format:

**Success:**
```json
{
  "command": "gh repo list",
  "return_code": 0,
  "elapsed": 1.234,
  "stdout": "...",
  "stderr": "",
  "result": "..."
}
```

**Error:**
```json
{
  "command": "gh invalid-command",
  "return_code": 1,
  "elapsed": 0.123,
  "stdout": "",
  "stderr": "error: unknown command",
  "result": "error: unknown command"
}
```

## Development

### Project Structure

```
smcp-plugin-github/
├── plugins/
│   ├── __init__.py
│   ├── gh/
│   │   ├── __init__.py
│   │   └── cli.py
│   └── git/
│       ├── __init__.py
│       └── cli.py
├── LICENSE
├── pyproject.toml
└── README.md
```

### Requirements

- Python 3.8+
- Standard library only (no external dependencies)

### Testing

The project includes a comprehensive test suite with 100% code coverage.

#### Install Test Dependencies

```bash
pip install -e ".[test]"
```

Or install directly:

```bash
pip install pytest pytest-cov pytest-mock pytest-timeout
```

#### Run Tests

**Run all unit tests (default):**
```bash
python tests/run_tests.py
```

Or using pytest directly:
```bash
pytest tests/ -v --cov=plugins --cov-report=term-missing --cov-fail-under=100
```

**Run specific test types:**
```bash
# Unit tests only
pytest tests/ -m unit -v

# Integration tests (requires gh/git CLI)
pytest tests/ -m integration -v

# End-to-end tests (requires gh/git CLI)
pytest tests/ -m e2e -v

# All tests
pytest tests/ -v
```

**Run with coverage report:**
```bash
pytest tests/ --cov=plugins --cov-report=html
# Open htmlcov/index.html in your browser
```

#### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual functions with mocked subprocess calls
- **Integration Tests** (`tests/integration/`): Test with real CLI tools (requires `gh`/`git` installed)
- **E2E Tests** (`tests/e2e/`): Test complete CLI workflows end-to-end

All tests are marked with pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.requires_gh` - Tests requiring GitHub CLI
- `@pytest.mark.requires_git` - Tests requiring Git CLI

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3).

See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Repository

- **GitHub**: [https://github.com/sanctumos/smcp-plugin-github](https://github.com/sanctumos/smcp-plugin-github)
- **Issues**: [https://github.com/sanctumos/smcp-plugin-github/issues](https://github.com/sanctumos/smcp-plugin-github/issues)

## Related Projects

- [SMCP](https://github.com/sanctumos/smcp) - Sanctum Letta MCP Server
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP Specification
