from pathlib import Path
from typing import Dict


class AliasParser:
    def __init__(self) -> None:
        self.aliases: Dict[str, str] = {}

    def load_aliases(self, directory: Path) -> None:
        """Load aliases from .mgit/alias file"""
        mgit_dir = directory / ".mgit"
        alias_file = mgit_dir / "alias"

        if alias_file.exists():
            with open(alias_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        folder_name, alias = line.split("=", 1)
                        self.aliases[folder_name.strip()] = alias.strip()

    def get_display_name(self, folder_name: str, use_real_name: bool = False) -> str:
        """Get display name for folder (alias or real name)"""
        if use_real_name or folder_name not in self.aliases:
            return folder_name
        return self.aliases[folder_name]
