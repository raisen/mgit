import shutil
from typing import List


def check_requirements() -> bool:
    """Check if git and gh are installed"""
    required_tools: List[str] = ["git", "gh"]
    missing_tools: List[str] = []

    for tool in required_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    if missing_tools:
        print(f"Error: Missing required tools: {', '.join(missing_tools)}")
        print("Please install git and GitHub CLI (gh)")
        return False

    return True
