from typing import List, Any, Tuple


class Colors:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

    @classmethod
    def green_icon(cls, text: str = "✓") -> str:
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def red_icon(cls, text: str = "✗") -> str:
        return f"{cls.RED}{text}{cls.RESET}"
    
    @classmethod
    def yellow_icon(cls, text: str = "↑") -> str:
        return f"{cls.YELLOW}{text}{cls.RESET}"
    
    @classmethod
    def gray_icon(cls, text: str = "?") -> str:
        return f"{cls.GRAY}{text}{cls.RESET}"


class RepoDisplay:
    def _get_sync_indicator(self, repo: Any) -> str:
        """Get sync status indicator based on repo sync status"""
        if hasattr(repo, 'sync_status'):
            sync_status = repo.sync_status
            status = sync_status.get("status", "unknown")
            
            if status == "synced":
                return Colors.green_icon()
            elif status == "ahead":
                return Colors.yellow_icon("↑")  # Local changes to push
            elif status == "behind":
                return Colors.red_icon("↓")     # Remote changes to pull
            elif status == "diverged":
                return Colors.red_icon("↕")     # Both ahead and behind
            else:
                return Colors.gray_icon("?")    # Unknown status
        else:
            # Fallback to old behavior
            if repo.is_remote_updated:
                return Colors.green_icon()
            else:
                return Colors.red_icon()

    def show_repos(self, repos: List[Any]) -> None:
        """Display repository information in a formatted table with correct alignment for ANSI codes"""
        import re
        if not repos:
            print("No git repositories found in current directory")
            return

        # Sort repos by display_name for consistent ordering with parallel mode
        repos = sorted(repos, key=lambda r: r.display_name)

        # Prepare all rows first to compute max visible length for each column
        rows: List[Tuple[str, str, str, str, str]] = []
        for repo in repos:
            unstaged = str(repo.unstaged_changes)
            branch = str(repo.current_branch)

            pr_info = repo.pr_info
            if pr_info and pr_info.get("exists", False):
                pr_number = pr_info.get("number")
                pr_url = pr_info.get("url")
                if pr_number and pr_url:
                    pr_status = f"\033]8;;{pr_url}\033\\{pr_number}\033]8;;\033\\"
                else:
                    pr_status = "Yes"
            else:
                pr_status = "No"

            remote_status = self._get_sync_indicator(repo)

            if repo.repo_url:
                repo_name = f"\033]8;;{repo.repo_url}\033\\{repo.display_name}\033]8;;\033\\"
            else:
                repo_name = repo.display_name

            rows.append((repo_name, unstaged, branch, pr_status, remote_status))

        # Calculate max visible length for each column
        def visible_len(s: str) -> int:
            return len(re.sub(r"\033\]8;;[^\033]*\033\\|\033\]8;;\033\\|\033\[[0-9;]*m", "", s))

        repo_w = max(30, max(visible_len(r[0]) for r in rows))
        unstaged_w = max(10, max(visible_len(r[1]) for r in rows))
        branch_w = max(20, max(visible_len(r[2]) for r in rows))
        pr_w = max(8, max(visible_len(r[3]) for r in rows))
        sync_w = max(14, max(visible_len(r[4]) for r in rows))

        def pad(s: str, w: int, align: str = "left") -> str:
            vlen = visible_len(s)
            if vlen >= w:
                return s
            pad_len = w - vlen
            if align == "left":
                return s + " " * pad_len
            elif align == "center":
                left = pad_len // 2
                right = pad_len - left
                return " " * left + s + " " * right
            else:
                return " " * pad_len + s

        # Print header using same padding logic
        header = (
            pad("Repository", repo_w) + " " +
            pad("Unstaged", unstaged_w) + " " +
            pad("Branch", branch_w) + " " +
            pad("PR", pr_w) + " " +
            pad("Sync", sync_w, "center")
        )
        print(header)
        print("-" * len(header))

        # Print rows
        for repo_name, unstaged, branch, pr_status, remote_status in rows:
            print(f"{pad(repo_name, repo_w)} {pad(unstaged, unstaged_w)} {pad(branch, branch_w)} {pad(pr_status, pr_w)} {pad(remote_status, sync_w, 'center')}")
