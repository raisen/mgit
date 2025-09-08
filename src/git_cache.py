import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


class GitCache:
    def __init__(self, working_dir: Optional[Union[str, Path]] = None) -> None:
        if working_dir is None:
            working_dir = Path.cwd()
        else:
            working_dir = Path(working_dir)

        self.cache_dir = working_dir / ".mgit"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "cache.json"
        self._cache_data: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_cache(self) -> None:
        """Save cache to disk"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self._cache_data, f, indent=2)
        except IOError:
            pass

    def _get_repo_key(self, repo_path: Path) -> str:
        """Generate unique key for repository"""
        return str(repo_path.absolute())

    def _get_git_mtime(self, repo_path: Path) -> float:
        """Get modification time of git index and HEAD"""
        git_dir = repo_path / ".git"
        times = []

        # Check .git/index (staging area changes)
        index_file = git_dir / "index"
        if index_file.exists():
            times.append(index_file.stat().st_mtime)

        # Check .git/HEAD (branch changes)
        head_file = git_dir / "HEAD"
        if head_file.exists():
            times.append(head_file.stat().st_mtime)

        # Check .git/refs directory (new commits)
        refs_dir = git_dir / "refs"
        if refs_dir.exists():
            for ref_file in refs_dir.rglob("*"):
                if ref_file.is_file():
                    times.append(ref_file.stat().st_mtime)

        return max(times) if times else 0.0

    def is_cached_valid(self, repo_path: Path) -> bool:
        """Check if cached data is still valid"""
        repo_key = self._get_repo_key(repo_path)
        if repo_key not in self._cache_data:
            return False

        cached_mtime = self._cache_data[repo_key].get("mtime", 0)
        current_mtime = self._get_git_mtime(repo_path)

        # Ensure we're comparing numbers
        if isinstance(cached_mtime, (int, float)) and isinstance(
            current_mtime, (int, float)
        ):
            return cached_mtime >= current_mtime
        return False

    def get_cached_data(self, repo_path: Path) -> Dict[str, Any]:
        """Get cached data for repository"""
        repo_key = self._get_repo_key(repo_path)
        repo_data = self._cache_data.get(repo_key, {})
        if isinstance(repo_data, dict):
            cached_data = repo_data.get("data", {})
            return cached_data if isinstance(cached_data, dict) else {}
        return {}

    def set_cache_data(self, repo_path: Path, data: Dict[str, Any]) -> None:
        """Cache data for repository"""
        repo_key = self._get_repo_key(repo_path)
        current_mtime = self._get_git_mtime(repo_path)

        self._cache_data[repo_key] = {"mtime": current_mtime, "data": data}
        self._save_cache()

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache_data = {}
        self._save_cache()
