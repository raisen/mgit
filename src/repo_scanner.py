from pathlib import Path
from typing import List
from git_utils import GitRepo
from exclude_parser import ExcludeParser
from alias_parser import AliasParser
from git_cache import GitCache


class RepoScanner:
    def __init__(self) -> None:
        self.exclude_parser = ExcludeParser()
        self.alias_parser = AliasParser()
        self.cache = GitCache()

    def scan_current_directory(self, use_real_names: bool = False) -> List[GitRepo]:
        """Scan current directory for git repositories"""
        current_dir = Path.cwd()
        excludes = self.exclude_parser.get_excludes(current_dir)
        self.alias_parser.load_aliases(current_dir)
        repos: List[GitRepo] = []

        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if self.exclude_parser.should_exclude(item.name, excludes):
                    continue

                git_dir = item / ".git"
                if git_dir.exists():
                    repo = GitRepo(item, self.alias_parser, use_real_names, self.cache)
                    repos.append(repo)

        # Save cache after processing all repos
        for repo in repos:
            repo._save_to_cache()  # type: ignore[attr-defined]

        return repos
