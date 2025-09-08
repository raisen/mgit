# mgit

A powerful CLI tool for managing multiple Git repositories simultaneously. Scan directories, check repository status, and perform bulk operations across all git repositories in your workspace.

## Features

- **Repository Discovery**: Automatically scans directories to find all git repositories
- **Parallel Processing**: Fast parallel execution for network operations
- **Status Overview**: Get a comprehensive view of all repositories' status
- **Bulk Operations**: Checkout branches, pull changes across multiple repos
- **Flexible Configuration**: Support for repository aliases and exclusions
- **Caching**: Intelligent caching for improved performance
- **Progress Display**: Real-time progress updates during operations

## Installation

### Prerequisites

- Python 3.9+
- Git
- GitHub CLI (`gh`) for GitHub integration features

### Install Dependencies

```bash
# Install all development dependencies (includes runtime dependencies)
make install-dev
```

### Make Executable

```bash
# Make the mgit script executable
chmod +x mgit
```

## Usage

### Using the Script (Development)

```bash
# Make executable and run
chmod +x mgit
./mgit status
```

### Using Standalone Executable (Production)

After building with `make build`:

```bash
# Run the standalone executable
./dist/mgit status
./dist/mgit checkout main
./dist/mgit pull
```

### Pre-built Releases

You can also download pre-built executables from the [GitHub Releases](https://github.com/yourusername/mgit/releases) page:

- **Linux**: `mgit-linux`
- **macOS**: `mgit-macos`
- **Windows**: `mgit-windows.exe`

These executables are automatically built and released when new versions are tagged.

### Basic Commands

```bash
# Show status of all repositories in current directory
./mgit status

# Show status with real folder names (not aliases)
./mgit status --names

# Clear cached data
./mgit status --clear-cache

# Use sequential processing instead of parallel
./mgit status --no-parallel

# Checkout a branch in all repositories
./mgit checkout main

# Pull latest changes in all repositories
./mgit pull

# Show help
./mgit --help
```

### Command Reference

| Command | Description |
|---------|-------------|
| `status` | Show repository status (default command) |
| `checkout <branch>` | Checkout specified branch in all repositories |
| `pull` | Pull latest changes in all repositories |

### Command Options

| Option | Description |
|--------|-------------|
| `-n, --names` | Show real folder names instead of aliases |
| `--clear-cache` | Clear cached repository data |
| `--no-parallel` | Use sequential processing instead of parallel |

## Configuration

### Repository Aliases

Create a `.mgit/alias` file in your working directory to define repository aliases:

```bash
# Create the .mgit directory and alias file
mkdir -p .mgit
cp alias_sample .mgit/alias
```

The alias file format is: `folder_name=display_alias`

```
# Example .mgit/alias file
core-tech-webapp=webapp
sales_demo_tool=demo
core-api-transcribe-service=transcribe
core-infrastructure=infra
```

### Repository Exclusions

Create a `.mgit/exclude` file to exclude specific directories:

```bash
# Create the exclude file
cp exclude_sample .mgit/exclude
```

The exclude file supports glob patterns:

```
# Example .mgit/exclude file
# Ignore specific repo folders
archived-projects
old-code
legacy

# Ignore temporary or backup repo folders
*-backup
*-old
*-archive

# Ignore all folders starting with underscore
_*
```

## Project Structure

```
mgit/
├── src/                  # Python source code
│   ├── main.py                 # CLI entry point
│   ├── git_utils.py           # Git operations wrapper
│   ├── git_cache.py           # Caching system
│   ├── repo_scanner.py        # Repository discovery
│   ├── parallel_processor.py  # Parallel processing
│   ├── progressive_display.py # Terminal display
│   ├── repo_display.py        # Repository display
│   ├── alias_parser.py        # Alias configuration
│   ├── exclude_parser.py      # Exclusion configuration
│   └── requirements.py        # Dependency checking
├── .mgit/               # User configuration (created by user)
│   ├── alias                  # Repository aliases
│   └── exclude                # Repository exclusions
├── .github/              # GitHub configuration
│   ├── workflows/             # GitHub Actions workflows
│   │   └── build-release.yml  # Automated build and release
│   └── copilot-instructions.md # Copilot instructions
├── pyproject.toml        # Project configuration
├── Makefile              # Development tasks
├── mgit                  # Executable script
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── alias_sample          # Alias configuration example
└── exclude_sample        # Exclusion configuration example
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Run linting and type checking
make check

# Run tests (if available)
make test
```

### Build Standalone Executable

```bash
# Build standalone executable with PyInstaller
make build

# The executable will be created at: dist/mgit
./dist/mgit --help

# Clean build artifacts
make clean-build
```

### Creating Releases

To create a new release with pre-built executables:

1. **Update version** in your code if needed
2. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **GitHub Actions will automatically**:
   - Build executables for Linux, macOS, and Windows
   - Create a GitHub release
   - Upload the executables as release assets

### Manual Release

You can also trigger a release manually using GitHub Actions workflow dispatch.

### Code Quality

This project uses:
- **mypy** for static type checking
- **ruff** for linting and formatting
- **Strict type checking** enabled

### Adding New Commands

1. Add command handler function in `main.py`
2. Add subparser for the command
3. Implement the logic in appropriate module
4. Update this README

### Adding Repository Operations

1. Add method to `GitRepo` class in `git_utils.py`
2. Follow the existing pattern for success/error handling
3. Add caching if appropriate
4. Update command handlers in `main.py`

## Architecture

### Core Components

- **GitRepo**: Wrapper around git operations with caching
- **RepoScanner**: Discovers git repositories in directory tree
- **ParallelProcessor**: Handles concurrent operations
- **ProgressiveDisplay**: Real-time terminal updates
- **GitCache**: File-based caching system

### Processing Flow

1. **Discovery**: Scan directory for `.git` folders
2. **Filtering**: Apply aliases and exclusions
3. **Fast Phase**: Local operations (status, branch info)
4. **Slow Phase**: Network operations (fetch, pull)
5. **Display**: Show results with progress updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure code quality
5. Submit a pull request

### Development Guidelines

- Follow existing code patterns and conventions
- Add type annotations for new code
- Update documentation for new features
- Test changes across different repository scenarios

## License

This project is open source. See LICENSE file for details.

## Troubleshooting

### Common Issues

**"gh command not found"**
- Install GitHub CLI: `brew install gh` (macOS) or follow [official installation guide](https://cli.github.com/)

**Permission denied on mgit script**
- Run: `chmod +x mgit`

**Python version issues**
- Ensure Python 3.9+ is installed and in PATH

**Cache issues**
- Clear cache with: `./mgit status --clear-cache`

### Getting Help

- Check the help: `./mgit --help`
- Review error messages for specific guidance
- Ensure all prerequisites are installed

## Changelog

### Version 1.0.0
- Initial release
- Repository scanning and status display
- Parallel processing support
- Checkout and pull commands
- Caching system
- Alias and exclusion support</content>
<parameter name="filePath">/Users/raisen/proj/amoofy/scripts/mgit/README.md