#!/usr/bin/env python3
"""
Quick script to add basic type hints to mgit files
"""

import re
from pathlib import Path


def add_basic_type_hints(file_path: Path) -> None:
    """Add basic type hints to a Python file"""
    with open(file_path, "r") as f:
        content = f.read()

    # Add return type annotations for functions that don't return anything
    content = re.sub(
        r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\):(\s*"""[^"]*?""")?\s*\n',
        r"def \1(\2) -> None:\3\n",
        content,
    )

    # Fix functions that actually return something
    patterns_with_returns = [
        (r"def (get_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (_get_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (check_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (should_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (create_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (format_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
        (r"def (pad_[a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\) -> None:", r"def \1(\2):"),
    ]

    for pattern, replacement in patterns_with_returns:
        content = re.sub(pattern, replacement, content)

    # Add parameter type hints for common patterns
    content = re.sub(
        r"def ([a-zA-Z_][a-zA-Z0-9_]*)\(self\):", r"def \1(self) -> None:", content
    )
    content = re.sub(
        r"def ([a-zA-Z_][a-zA-Z0-9_]*)\(self\) -> None -> None:",
        r"def \1(self) -> None:",
        content,
    )

    with open(file_path, "w") as f:
        f.write(content)


def main() -> None:
    """Main function to process all Python files"""
    mgit_dir = Path(".")

    for py_file in mgit_dir.glob("*.py"):
        if py_file.name not in ["add_types.py"]:  # Skip this script itself
            print(f"Processing {py_file}")
            add_basic_type_hints(py_file)

    print("Basic type hints added. You may need to manually fix some return types.")


if __name__ == "__main__":
    main()
