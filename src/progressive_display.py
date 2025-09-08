import sys
from typing import Dict, Any, Optional
import re


class ProgressiveDisplay:
    def __init__(self) -> None:
        self.header_printed = False
        self.repo_lines: Dict[str, Any] = {}
        self.current_line = 0
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0

    def create_hyperlink(self, url: Optional[str], text: str) -> str:
        """Create OSC 8 hyperlink"""
        if url and text:
            return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
        return text

    def _get_sync_indicator(self, result: Any) -> str:
        """Get sync status indicator based on result sync status"""
        if result.sync_status is not None:
            sync_status = result.sync_status
            status = sync_status.get("status", "unknown")
            
            if status == "synced":
                return "\033[32m✓\033[0m"      # Green checkmark
            elif status == "ahead":
                return "\033[33m↑\033[0m"      # Yellow up arrow (local changes to push)
            elif status == "behind":
                return "\033[31m↓\033[0m"      # Red down arrow (remote changes to pull)
            elif status == "diverged":
                return "\033[31m↕\033[0m"      # Red up-down arrow (diverged)
            else:
                return "\033[90m?\033[0m"      # Gray question mark (unknown)
        elif result.is_remote_updated is not None:
            # Fallback to old behavior
            if result.is_remote_updated:
                return "\033[32m✓\033[0m"      # Green checkmark
            else:
                return "\033[31m✗\033[0m"      # Red X
        else:
            return "\033[90m?\033[0m"          # Gray question mark for errors

    def pad_with_ansi(self, text: str, width: int, align: str = "left") -> str:
        """Pad text that may contain ANSI sequences to specified display width"""
        # Calculate visible character count (excluding ANSI sequences)
        import re

        visible_text = re.sub(
            r"\033\]8;;[^\033]*\033\\|\033\]8;;\033\\|\033\[[0-9;]*m", "", text
        )
        visible_len = len(visible_text)

        if visible_len >= width:
            return text

        padding = width - visible_len
        if align == "left":
            return text + " " * padding
        elif align == "center":
            left_padding = padding // 2
            right_padding = padding - left_padding
            return " " * left_padding + text + " " * right_padding
        else:  # right align
            return " " * padding + text

    def clear_screen(self) -> None:
        """Clear screen and reset cursor"""
        print("\033[2J\033[H", end="")

    def move_to_line(self, line_num: int) -> None:
        """Move cursor to specific line"""
        print(f"\033[{line_num};1H", end="")

    def clear_to_end_of_line(self) -> None:
        """Clear from cursor to end of line"""
        print("\033[K", end="")

    def print_header(self, repo_w: int, unstaged_w: int, branch_w: int, pr_w: int, sync_w: int) -> None:
        """Print table header with given column widths"""
        # Only clear screen and print header once
        if not self.header_printed:
            self.clear_screen()
            header = (
                f"{('Repository'):<{repo_w}} "
                f"{('Unstaged'):<{unstaged_w}} "
                f"{('Branch'):<{branch_w}} "
                f"{('PR'):<{pr_w}} "
                f"{('Sync'):^{sync_w}}"
            )
            print(header)
            print("-" * len(header))
            self.header_printed = True
            self.current_line = 3

    def format_repo_line(self, result: Any) -> str:
        """Format a repository line for display"""
        # Keep this for backward compatibility but not used by new update_display
        return ""

    def update_display(self, results: Dict[str, Any], phase: str = "") -> None:
        """Update the display with current results"""
        # Build rows first to compute dynamic widths (ANSI-aware)
        sorted_results = sorted(results.values(), key=lambda r: r.display_name)
        rows = []
        for result in sorted_results:
            spinner_char = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]

            # unstaged
            if result.unstaged_changes is not None:
                unstaged = str(result.unstaged_changes)
            elif result.errors and "unstaged" in result.errors:
                unstaged = "Error"
            else:
                unstaged = spinner_char

            # branch
            if result.current_branch is not None:
                branch = result.current_branch
            elif result.errors and "branch" in result.errors:
                branch = "Error"
            else:
                branch = spinner_char

            # pr
            if result.pr_info is not None:
                if result.pr_info.get("exists", False):
                    pr_number = result.pr_info.get("number")
                    pr_url = result.pr_info.get("url")
                    if pr_number and pr_url:
                        pr_status = self.create_hyperlink(pr_url, str(pr_number))
                    else:
                        pr_status = "Yes"
                else:
                    pr_status = "No"
            elif result.errors and "pr" in result.errors:
                pr_status = "Error"
            else:
                pr_status = spinner_char

            # remote
            if result.sync_status is not None or result.is_remote_updated is not None:
                remote_status = self._get_sync_indicator(result)
            elif result.errors and "remote" in result.errors:
                remote_status = "Error"
            else:
                remote_status = spinner_char

            # repo name
            if result.repo_url:
                repo_name = self.create_hyperlink(result.repo_url, result.display_name)
            else:
                repo_name = result.display_name

            rows.append((repo_name, unstaged, branch, pr_status, remote_status))

        # ANSI-aware visible length helper
        def visible_len(s: str) -> int:
            return len(re.sub(r"\033\]8;;[^\033]*\033\\|\033\]8;;\033\\|\033\[[0-9;]*m", "", s))

        repo_w = max(30, max(visible_len(r[0]) for r in rows) if rows else 30)
        unstaged_w = max(10, max(visible_len(r[1]) for r in rows) if rows else 10)
        branch_w = max(20, max(visible_len(r[2]) for r in rows) if rows else 20)
        pr_w = max(8, max(visible_len(r[3]) for r in rows) if rows else 8)
        sync_w = max(14, max(visible_len(r[4]) for r in rows) if rows else 14)

        # Print header with computed widths
        self.print_header(repo_w, unstaged_w, branch_w, pr_w, sync_w)

        # Render each row
        for i, (repo_name, unstaged, branch, pr_status, remote_status) in enumerate(rows):
            line_num = 3 + i
            self.move_to_line(line_num)
            self.clear_to_end_of_line()

            repo_col = self.pad_with_ansi(repo_name, repo_w)
            unstaged_col = self.pad_with_ansi(str(unstaged), unstaged_w)
            branch_col = self.pad_with_ansi(str(branch), branch_w)
            pr_col = self.pad_with_ansi(str(pr_status), pr_w)
            remote_col = self.pad_with_ansi(remote_status, sync_w, "center")

            line_content = f"{repo_col} {unstaged_col} {branch_col} {pr_col} {remote_col}"
            print(line_content, end="")

        # Update spinner for next display refresh
        self.spinner_index += 1
        sys.stdout.flush()

    def final_display(self, results: Dict[str, Any]) -> None:
        """Display final results without progress indicators"""
        self.update_display(results)

        # Move cursor to the end
        final_line = len(results) + 4
        self.move_to_line(final_line)

        print()  # Add final newline
