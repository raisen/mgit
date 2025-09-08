import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, cast
from git_cache import GitCache


class GitRepo:
    def __init__(
        self,
        repo_path: Path,
        alias_parser: Optional[Any] = None,
        use_real_names: bool = False,
        cache: Optional[GitCache] = None,
    ) -> None:
        self.path = repo_path
        self.real_name = repo_path.name
        self.alias_parser = alias_parser
        self.use_real_names = use_real_names
        self.cache = cache or GitCache()
        self._cached_data: Dict[str, Any] = {}
        self._load_cached_data()

    def _load_cached_data(self) -> None:
        """Load cached data if available and valid"""
        if self.cache.is_cached_valid(self.path):
            cached = self.cache.get_cached_data(self.path)
            self._cached_data = cached
        else:
            self._cached_data = {}

    def _save_to_cache(self) -> None:
        """Save current data to cache"""
        data: Dict[str, Any] = {}
        if "unstaged_changes" in self._cached_data:
            data["unstaged_changes"] = self._cached_data["unstaged_changes"]
        if "current_branch" in self._cached_data:
            data["current_branch"] = self._cached_data["current_branch"]
        if "pr_info" in self._cached_data:
            data["pr_info"] = self._cached_data["pr_info"]
        if "is_remote_updated" in self._cached_data:
            data["is_remote_updated"] = self._cached_data["is_remote_updated"]
        if "sync_status" in self._cached_data:
            data["sync_status"] = self._cached_data["sync_status"]
        if "repo_url" in self._cached_data:
            data["repo_url"] = self._cached_data["repo_url"]

        # Only cache if we have some data
        if data:
            self.cache.set_cache_data(self.path, data)

    @property
    def unstaged_changes(self) -> int:
        if "unstaged_changes" in self._cached_data:
            cached_value = self._cached_data["unstaged_changes"]
            return cached_value if isinstance(cached_value, int) else 0
        result = self._get_unstaged_changes()
        self._cached_data["unstaged_changes"] = result
        return result

    @property
    def current_branch(self) -> str:
        if "current_branch" in self._cached_data:
            cached_value = self._cached_data["current_branch"]
            return cached_value if isinstance(cached_value, str) else "unknown"
        result = self._get_current_branch()
        self._cached_data["current_branch"] = result
        return result

    @property
    def pr_info(self) -> Dict[str, Any]:
        if "pr_info" in self._cached_data:
            cached_value = self._cached_data["pr_info"]
            if isinstance(cached_value, dict):
                return cast(Dict[str, Any], cached_value)
            return {"exists": False, "number": None, "url": None}
        result = self._check_pr_exists()
        self._cached_data["pr_info"] = result
        return result



    @property
    def is_remote_updated(self) -> bool:
        if "is_remote_updated" in self._cached_data:
            cached_value = self._cached_data["is_remote_updated"]
            return cached_value if isinstance(cached_value, bool) else False
        result = self._check_remote_updated()
        self._cached_data["is_remote_updated"] = result
        return result

    @property
    def sync_status(self) -> Dict[str, Any]:
        if "sync_status" in self._cached_data:
            cached_value = self._cached_data["sync_status"]
            if isinstance(cached_value, dict):
                return cast(Dict[str, Any], cached_value)
            return {"status": "unknown", "ahead": 0, "behind": 0}
        result = self._get_sync_status()
        self._cached_data["sync_status"] = result
        return result

    @property
    def repo_url(self) -> Optional[str]:
        if "repo_url" in self._cached_data:
            cached_value = self._cached_data["repo_url"]
            return (
                cached_value
                if isinstance(cached_value, str) or cached_value is None
                else None
            )
        result = self._get_repo_url()
        self._cached_data["repo_url"] = result
        return result

    def _run_git_command(self, args: list[str]) -> Optional[str]:
        """Run git command in repo directory"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _run_gh_command(self, args: list[str]) -> Optional[str]:
        """Run gh command in repo directory"""
        try:
            result = subprocess.run(
                ["gh"] + args, cwd=self.path, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _get_unstaged_changes(self) -> int:
        """Get number of unstaged changes"""
        output = self._run_git_command(["status", "--porcelain"])
        if output is None:
            return 0

        lines = output.split("\n")
        unstaged_count = 0
        for line in lines:
            if line and (line[1] in ["M", "D", "A", "?"] or line[0] == "?"):
                unstaged_count += 1
        return unstaged_count

    def _get_current_branch(self) -> str:
        """Get current branch name"""
        branch = self._run_git_command(["branch", "--show-current"])
        return branch if branch else "detached"

    def _get_repo_url(self) -> Optional[str]:
        """Get the repository URL"""
        output = self._run_gh_command(["repo", "view", "--json", "url"])
        if output:
            try:
                repo_data = json.loads(output)
                url = repo_data.get("url")
                return url if isinstance(url, str) else None
            except json.JSONDecodeError:
                pass
        return None

    def _check_pr_exists(self) -> Dict[str, Any]:
        """Check if PR exists for current branch and return PR info"""
        output = self._run_gh_command(
            ["pr", "list", "--head", self.current_branch, "--json", "number,url"]
        )
        if output:
            try:
                prs = json.loads(output)
                if len(prs) > 0:
                    # Return the first PR's info
                    pr = prs[0]
                    return {
                        "exists": True,
                        "number": pr.get("number"),
                        "url": pr.get("url"),
                    }
            except json.JSONDecodeError:
                pass
        return {"exists": False, "number": None, "url": None}

    def _check_remote_updated(self) -> bool:
        """Check if remote is up to date with local (backward compatibility)"""
        sync_status = self._get_sync_status()
        return str(sync_status.get("status", "")) == "synced"

    def _get_sync_status(self) -> Dict[str, Any]:
        """Get detailed sync status with remote"""
        self._run_git_command(["fetch"])

        local_commit = self._run_git_command(["rev-parse", self.current_branch])
        remote_commit = self._run_git_command(
            ["rev-parse", f"origin/{self.current_branch}"]
        )

        if not local_commit:
            return {"status": "unknown", "ahead": 0, "behind": 0}
        
        if not remote_commit:
            # Remote branch doesn't exist, we have local commits to push
            return {"status": "ahead", "ahead": 1, "behind": 0}

        if local_commit == remote_commit:
            return {"status": "synced", "ahead": 0, "behind": 0}

        # Check if we're ahead (have local commits to push)
        ahead_output = self._run_git_command([
            "rev-list", "--count", f"origin/{self.current_branch}..{self.current_branch}"
        ])
        ahead_count = int(ahead_output) if ahead_output and ahead_output.isdigit() else 0

        # Check if we're behind (have remote commits to pull)
        behind_output = self._run_git_command([
            "rev-list", "--count", f"{self.current_branch}..origin/{self.current_branch}"
        ])
        behind_count = int(behind_output) if behind_output and behind_output.isdigit() else 0

        if ahead_count > 0 and behind_count > 0:
            return {"status": "diverged", "ahead": ahead_count, "behind": behind_count}
        elif ahead_count > 0:
            return {"status": "ahead", "ahead": ahead_count, "behind": 0}
        elif behind_count > 0:
            return {"status": "behind", "ahead": 0, "behind": behind_count}
        else:
            return {"status": "synced", "ahead": 0, "behind": 0}

    def checkout_branch(self, branch_name: str) -> Dict[str, Any]:
        """Checkout a branch and return result status"""
        try:
            # Check if branch exists locally
            existing_branches = self._run_git_command(["branch", "--list", branch_name])

            if existing_branches:
                # Branch exists locally, just checkout
                result = self._run_git_command(["checkout", branch_name])
                if result is not None:
                    # Update cached current_branch after successful checkout
                    self._cached_data["current_branch"] = branch_name
                    return {
                        "success": True,
                        "message": f"Switched to branch '{branch_name}'",
                        "created": False,
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to checkout existing branch '{branch_name}'",
                        "created": False,
                    }
            else:
                # Check if branch exists on remote
                remote_branches = self._run_git_command(
                    ["branch", "-r", "--list", f"origin/{branch_name}"]
                )

                if remote_branches:
                    # Branch exists on remote, create and checkout with tracking
                    result = self._run_git_command(
                        ["checkout", "-b", branch_name, f"origin/{branch_name}"]
                    )
                    if result is not None:
                        # Update cached current_branch after successful checkout
                        self._cached_data["current_branch"] = branch_name
                        return {
                            "success": True,
                            "message": f"Created and switched to branch '{branch_name}' tracking origin/{branch_name}",
                            "created": True,
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Failed to checkout remote branch '{branch_name}'",
                            "created": False,
                        }
                else:
                    # Branch doesn't exist anywhere, create new local branch
                    result = self._run_git_command(["checkout", "-b", branch_name])
                    if result is not None:
                        # Update cached current_branch after successful checkout
                        self._cached_data["current_branch"] = branch_name
                        return {
                            "success": True,
                            "message": f"Created and switched to new branch '{branch_name}'",
                            "created": True,
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Failed to create new branch '{branch_name}'",
                            "created": False,
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during checkout: {str(e)}",
                "created": False,
            }

    def pull(self) -> Dict[str, Any]:
        """Pull latest changes for current branch"""
        try:
            result = self._run_git_command(["pull"])
            if result is not None:
                return {
                    "success": True,
                    "message": f"Successfully pulled latest changes for branch '{self.current_branch}'",
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to pull changes for branch '{self.current_branch}'",
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during pull: {str(e)}",
            }

    @property
    def display_name(self) -> str:
        """Get display name (alias or real name)"""
        if self.alias_parser:
            display_name = self.alias_parser.get_display_name(
                self.real_name, self.use_real_names
            )
            return display_name if isinstance(display_name, str) else self.real_name
        return self.real_name
