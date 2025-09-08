#!/usr/bin/env python3

import sys
import argparse
from requirements import check_requirements
from repo_scanner import RepoScanner
from repo_display import RepoDisplay
from parallel_processor import ParallelRepoProcessor
from progressive_display import ProgressiveDisplay
from typing import List, Any


def checkout_branch_in_all_repos(repos: List[Any], branch_name: str) -> None:
    """Checkout specified branch in all repositories"""
    print(f"Checking out branch '{branch_name}' in all repositories...")
    print()

    success_count = 0
    error_count = 0

    for repo in repos:
        print(f"Processing {repo.display_name}...", end=" ")

        try:
            result = repo.checkout_branch(branch_name)

            if result["success"]:
                success_count += 1
                if result["created"]:
                    print("✓ " + result["message"])
                else:
                    print("✓ " + result["message"])
            else:
                error_count += 1
                print("✗ " + result["message"])

        except Exception as e:
            error_count += 1
            print(f"✗ Error: {str(e)}")

    print()
    print(
        f"Summary: {success_count} successful, {error_count} failed out of {len(repos)} repositories"
    )

    if error_count > 0:
        sys.exit(1)


def pull_all_repos(repos: List[Any]) -> None:
    """Pull latest changes in all repositories"""
    print("Pulling latest changes in all repositories...")
    print()

    success_count = 0
    error_count = 0

    for repo in repos:
        print(f"Processing {repo.display_name}...", end=" ")

        try:
            result = repo.pull()

            if result["success"]:
                success_count += 1
                print("✓ " + result["message"])
            else:
                error_count += 1
                print("✗ " + result["message"])

        except Exception as e:
            error_count += 1
            print(f"✗ Error: {str(e)}")

    print()
    print(
        f"Summary: {success_count} successful, {error_count} failed out of {len(repos)} repositories"
    )

    if error_count > 0:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage multiple git repositories")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Default status command (no subcommand)
    status_parser = subparsers.add_parser(
        "status", help="Show repository status (default)"
    )
    status_parser.add_argument(
        "-n",
        "--names",
        action="store_true",
        help="Show real folder names instead of aliases",
    )
    status_parser.add_argument(
        "--clear-cache", action="store_true", help="Clear cached repository data"
    )
    status_parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing (use original sequential mode)",
    )

    # Checkout command
    checkout_parser = subparsers.add_parser(
        "checkout", help="Checkout branch in all repositories"
    )
    checkout_parser.add_argument(
        "branch", help="Branch name to checkout in all repositories"
    )
    checkout_parser.add_argument(
        "-n",
        "--names",
        action="store_true",
        help="Show real folder names instead of aliases",
    )

    # Pull command
    pull_parser = subparsers.add_parser(
        "pull", help="Pull latest changes in all repositories"
    )
    pull_parser.add_argument(
        "-n",
        "--names",
        action="store_true",
        help="Show real folder names instead of aliases",
    )

    # Add top-level flags for backwards compatibility (when no subcommand is used)
    parser.add_argument(
        "-n",
        "--names",
        action="store_true",
        help="Show real folder names instead of aliases",
    )
    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear cached repository data"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing (use original sequential mode)",
    )

    args = parser.parse_args()

    # If no command specified, default to status behavior
    if args.command is None:
        args.command = "status"

    if not check_requirements():
        sys.exit(1)

    scanner = RepoScanner()

    if args.command == "status":
        if args.clear_cache:
            scanner.cache.clear_cache()
            print("Cache cleared.")
            return

        repos = scanner.scan_current_directory(use_real_names=args.names)

        if args.no_parallel:
            # Original sequential mode
            display = RepoDisplay()
            display.show_repos(repos)
        else:
            # New parallel mode with progressive display
            progressive_display = ProgressiveDisplay()
            processor = ParallelRepoProcessor(repos)

            # Process with live updates
            results = processor.process_all(
                display_callback=lambda results,
                phase: progressive_display.update_display(results, phase)
            )

            # Show final results
            progressive_display.final_display(results)

    elif args.command == "checkout":
        repos = scanner.scan_current_directory(use_real_names=args.names)
        checkout_branch_in_all_repos(repos, args.branch)

    elif args.command == "pull":
        repos = scanner.scan_current_directory(use_real_names=args.names)
        pull_all_repos(repos)


if __name__ == "__main__":
    main()
