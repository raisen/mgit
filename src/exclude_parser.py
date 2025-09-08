import fnmatch
from pathlib import Path
from typing import List


class ExcludeParser:
    def get_excludes(self, directory: Path) -> List[str]:
        """Read exclude file from .mgit folder if it exists"""
        mgit_dir = directory / ".mgit"
        exclude_file = mgit_dir / "exclude"
        excludes: List[str] = []

        if exclude_file.exists():
            with open(exclude_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        excludes.append(line)

        return excludes

    def should_exclude(self, folder_name: str, excludes: List[str]) -> bool:
        """Check if folder should be excluded based on patterns"""
        for pattern in excludes:
            if fnmatch.fnmatch(folder_name, pattern):
                return True
        return False
