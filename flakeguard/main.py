"""
main.py — FlakeGuard Entry Point

This is what GitHub Actions runs when a PR is opened.
It ties together the analyzer and reporter, and posts
the result as a comment on the pull request.
"""

import os
import sys
from github import Github
from flakeguard.analyzer import analyze_files
from flakeguard.reporter import format_full_report


# ─────────────────────────────────────────
# Get changed test files from the PR
# ─────────────────────────────────────────
def get_changed_test_files(repo, pr_number):
    """
    Fetch the list of files changed in a PR
    and return only test files (files starting
    with test_ or ending with _test.py).
    """
    pr = repo.get_pull(pr_number)
    changed_files = pr.get_files()

    test_files = []
    for f in changed_files:
        filename = f.filename
        basename = os.path.basename(filename)

        # Only include Python test files
        if filename.endswith(".py"):
            if basename.startswith("test_") or basename.endswith("_test.py"):
                test_files.append(filename)

    return pr, test_files


# ─────────────────────────────────────────
# Post a comment on the PR
# ─────────────────────────────────────────
def post_comment(pr, report):
    """
    Post the FlakeGuard report as a comment on the PR.
    If a FlakeGuard comment already exists, update it
    instead of posting a duplicate.
    """
    # Check if we already commented on this PR
    for comment in pr.get_issue_comments():
        if "FlakeGuard Report" in comment.body:
            # Update existing comment
            comment.edit(report)
            print("Updated existing FlakeGuard comment.")
            return

    # Post a new comment
    pr.create_issue_comment(report)
    print("Posted new FlakeGuard comment.")


# ─────────────────────────────────────────
# Main function
# ─────────────────────────────────────────
def main():
    # Step 1: Read environment variables set by GitHub Actions
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name    = os.environ.get("GITHUB_REPOSITORY")  # e.g. "myafine/flakeguard"
    pr_number    = os.environ.get("PR_NUMBER")

    # Validate
    if not all([github_token, repo_name, pr_number]):
        print("Missing environment variables. Required: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER")
        sys.exit(1)

    pr_number = int(pr_number)

    # Step 2: Connect to GitHub
    print(f"Connecting to GitHub repo: {repo_name}, PR #{pr_number}")
    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # Step 3: Get changed test files
    pr, test_files = get_changed_test_files(repo, pr_number)

    if not test_files:
        print("No test files changed in this PR. Skipping FlakeGuard.")
        sys.exit(0)

    print(f"Found {len(test_files)} test file(s) to analyze:")
    for f in test_files:
        print(f"  - {f}")

    # Step 4: Run the analyzer
    results = analyze_files(test_files)

    # Step 5: Format the report
    report = format_full_report(results)
    print("\n--- Generated Report ---")
    print(report)
    print("------------------------\n")

    # Step 6: Post comment on PR
    post_comment(pr, report)
    print("Done!")


if __name__ == "__main__":
    main()