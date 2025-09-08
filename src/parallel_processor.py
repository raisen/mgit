import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Callable, Tuple


@dataclass
class RepoResult:
    name: str
    display_name: str
    unstaged_changes: Optional[int] = None
    current_branch: Optional[str] = None
    pr_info: Optional[Dict[str, Any]] = None
    is_remote_updated: Optional[bool] = None
    sync_status: Optional[Dict[str, Any]] = None
    repo_url: Optional[str] = None
    errors: Optional[Dict[str, str]] = None

    @property
    def has_pr(self) -> bool:
        """Backward compatibility property"""
        return bool(self.pr_info and self.pr_info.get("exists", False))

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = {}


class ParallelRepoProcessor:
    def __init__(self, repos: List[Any], max_workers: int = 8) -> None:
        self.repos = repos
        self.max_workers = max_workers
        self.results: Dict[str, RepoResult] = {}
        self.completed_count = 0
        self.total_count = len(repos)
        self.display_lock = threading.Lock()

    def process_repo_fast(self, repo: Any) -> RepoResult:
        """Process fast local git operations"""
        result = RepoResult(repo.real_name, repo.display_name)
        if result.errors is None:
            result.errors = {}

        try:
            result.unstaged_changes = repo._get_unstaged_changes()
        except Exception as e:
            result.errors["unstaged"] = str(e)

        try:
            result.current_branch = repo._get_current_branch()
        except Exception as e:
            result.errors["branch"] = str(e)

        return result

    def process_repo_slow(self, repo: Any) -> Tuple[str, Dict[str, Any]]:
        """Process slow network operations"""
        updates = {}

        try:
            updates["pr_info"] = repo._check_pr_exists()
        except Exception as e:
            updates["pr_error"] = str(e)

        try:
            updates["is_remote_updated"] = repo._check_remote_updated()
            updates["sync_status"] = repo._get_sync_status()
        except Exception as e:
            updates["remote_error"] = str(e)

        try:
            updates["repo_url"] = repo._get_repo_url()
        except Exception as e:
            updates["repo_url_error"] = str(e)

        return repo.real_name, updates

    def update_result(self, repo_name: str, updates: Dict[str, Any]) -> None:
        """Thread-safe result update"""
        with self.display_lock:
            if repo_name in self.results:
                result = self.results[repo_name]
                for key, value in updates.items():
                    if key.endswith("_error"):
                        error_key = key.replace("_error", "")
                        if result.errors is not None:
                            result.errors[error_key] = value
                    else:
                        setattr(result, key, value)

    def process_all(
        self,
        display_callback: Optional[Callable[[Dict[str, RepoResult], str], None]] = None,
    ) -> Dict[str, RepoResult]:
        """Process all repositories with parallel execution"""
        # Phase 1: Fast local operations
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_repo = {
                executor.submit(self.process_repo_fast, repo): repo
                for repo in self.repos
            }

            for future in as_completed(future_to_repo):
                result = future.result()
                with self.display_lock:
                    self.results[result.name] = result
                    self.completed_count += 1

                if display_callback:
                    display_callback(self.results, "fast")

        # Phase 2: Slow network operations
        self._process_slow_operations(display_callback)

        return self.results

    def _process_slow_operations(
        self, display_callback: Optional[Callable[[Dict[str, RepoResult], str], None]]
    ) -> None:
        """Process slow network operations in separate executor"""
        with ThreadPoolExecutor(max_workers=min(4, self.max_workers)) as executor:
            # Submit all slow operations
            futures = [
                executor.submit(self.process_repo_slow, repo) for repo in self.repos
            ]

            # Process results as they complete
            for future in as_completed(futures):
                repo_name, updates = (
                    future.result()
                )  # We know this returns Tuple[str, Dict[str, Any]]
                self.update_result(repo_name, updates)

                if display_callback:
                    display_callback(self.results, "slow")
