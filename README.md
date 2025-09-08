# mgit

A command-line tool for managing multiple Git repositories simultaneously. Scan directories, check repository status, and perform bulk operations across all Git repositories in your workspace.

## Features

- **Repository Discovery**: Automatically scans directories to find Git repositories
- **Parallel Processing**: Fast parallel execution for network operations
- **Status Overview**: Comprehensive view of all repositories' status
- **Bulk Operations**: Checkout branches and pull changes across multiple repositories
- **Configuration**: Support for repository aliases and exclusions
- **Caching**: Intelligent caching for improved performance
- **Progress Display**: Real-time progress updates during operations

## Installation

### Prerequisites

- Python 3.9+
- Git
- GitHub CLI (`gh`) for GitHub integration features

### Quick Setup

```bash
# Install dependencies
cd mgit-src
make install-dev

# Make executable
chmod +x mgit
```

### Pre-built Executables

Download pre-built executables from [GitHub Releases](https://github.com/raisen/mgit/releases):

## Usage

### Basic Commands

```bash
# Show status of all repositories
./mgit status

# Show status with real folder names
./mgit status --names

# Clear cached data
./mgit status --clear-cache

# Checkout a branch in all repositories
./mgit checkout main

# Pull latest changes in all repositories
./mgit pull

# Show help
./mgit --help
```

### Command Options

| Option | Description |
|--------|-------------|
| `-n, --names` | Show real folder names instead of aliases |
| `--clear-cache` | Clear cached repository data |
| `--no-parallel` | Use sequential processing instead of parallel |

## Configuration

### Repository Aliases

Create a `.mgit/alias` file to define repository aliases:

```
# Example .mgit/alias file
full-folder-name=short-name
```

### Repository Exclusions

Create a `.mgit/exclude` file to exclude specific directories:

```bash
cp exclude_sample .mgit/exclude
```

Supports glob patterns:

```
# Example .mgit/exclude file
archived-projects
*-backup
_*
```

## Development

### Setup

```bash
# Install development dependencies
make install-dev

# Run checks
make check

# Build standalone executable
make build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure code quality
5. Submit a pull request