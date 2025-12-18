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
- **Error Handling**: Robust error handling with detailed output capture
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
