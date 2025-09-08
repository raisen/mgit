# Makefile for mgit project

# Variables
PYTHON := python3
MGIT_DIR := .
SRC_FILES := $(MGIT_DIR)/src/*.py

# Default target
.DEFAULT_GOAL := help

# Help target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Install development dependencies
install-dev: ## Install development dependencies (ruff, mypy, pyinstaller)
	@echo "Installing development dependencies..."
	pip3 install ruff mypy pyinstaller

# Build standalone executable
build: ## Build standalone executable with PyInstaller
	@echo "Building standalone executable..."
	@echo "This will create a single executable file in dist/ directory"
	pyinstaller --onefile --name mgit \
		--paths src \
		--hidden-import concurrent.futures \
		--hidden-import concurrent \
		--hidden-import subprocess \
		--hidden-import json \
		--hidden-import pathlib \
		--hidden-import argparse \
		--hidden-import typing \
		mgit
	@echo "Build complete! Executable created at: dist/mgit"
	@echo "You can run it with: ./dist/mgit --help"

# Clean build artifacts
clean-build: ## Clean build artifacts and dist directory
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -f mgit.spec

# Lint with ruff
lint: ## Run ruff linter on mgit code
	@echo "Running ruff linter..."
	ruff check $(SRC_FILES)

# Format code with ruff
format: ## Format code with ruff
	@echo "Formatting code with ruff..."
	ruff format $(SRC_FILES)

# Type check with mypy
typecheck: ## Run mypy type checker
	@echo "Running mypy type checker..."
	mypy $(SRC_FILES) --strict --ignore-missing-imports

# Run all checks
check: lint typecheck ## Run all linting and type checking

# Fix common issues automatically
fix: ## Automatically fix common issues with ruff
	@echo "Auto-fixing issues with ruff..."
	ruff check --fix $(SRC_FILES)
	ruff format $(SRC_FILES)

# Clean cache files
clean: ## Clean up cache files and temporary files
	@echo "Cleaning cache files..."
	find $(MGIT_DIR) -type f -name "*.pyc" -delete
	find $(MGIT_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(MGIT_DIR) -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(MGIT_DIR) -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/
	rm -f mgit.spec

# Test mgit (dry run)
test: ## Test mgit script
	@echo "Testing mgit script..."
	cd $(CURDIR) && $(PYTHON) $(MGIT_DIR)/mgit --help

# Full workflow: clean, install, format, check
all: clean install-dev format check ## Run complete workflow: clean, install deps, format, and check

.PHONY: help install-dev lint format typecheck check fix clean test all build clean-build