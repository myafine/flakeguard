"""
reporter.py — GitHub PR Comment Formatter

Takes a dict of warnings from analyzer.py and formats
them into a clean markdown comment for GitHub PRs.
"""


# ─────────────────────────────────────────
# Format warnings for a single file
# ─────────────────────────────────────────
def format_file_report(filepath, warnings):
    """
    Format warnings for one file into a markdown table.
    """
    lines = []

    # File header
    lines.append(f"### `{filepath}`")
    lines.append("")

    # Table header
    lines.append("| Line | Test Function | Warning |")
    lines.append("|------|--------------|---------|")

    # One row per warning
    for w in warnings:
        # Truncate long messages for the table
        short_msg = w.message[:120] + "..." if len(w.message) > 120 else w.message
        lines.append(f"| {w.line} | `{w.test_name}` | {short_msg} |")

    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────
# Format the full report for all files
# ─────────────────────────────────────────
def format_full_report(results):
    """
    Format warnings for all files into one GitHub PR comment.

    results: dict { filepath: [Warning, ...] }
    """
    # Count total warnings
    total = sum(len(w) for w in results.values())

    lines = []

    # Header
    lines.append("## FlakeGuard Report")
    lines.append("")

    # Summary box
    if total == 0:
        lines.append("> All tests look clean! No flakiness signals detected.")
        lines.append("")
        lines.append("---")
        lines.append("_Powered by FlakeGuard_")
        return "\n".join(lines)

    lines.append(f"> **{total} potential flakiness issue(s)** detected across "
                 f"**{len(results)} file(s)**. Please review before merging.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-file reports
    for filepath, warnings in results.items():
        lines.append(format_file_report(filepath, warnings))

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("**What should I do?**")
    lines.append("")
    lines.append("- **sleep() / time dependencies** -> replace with event-driven waits or mocks")
    lines.append("- **Network calls** -> use `unittest.mock` or `responses` library to mock HTTP")
    lines.append("- **Randomness** -> set a fixed seed with `random.seed(42)`")
    lines.append("- **Date/time** -> use `freezegun` to freeze time in tests")
    lines.append("- **Env variables** -> use `monkeypatch` or `mock.patch.dict`")
    lines.append("")
    lines.append("_Powered by FlakeGuard_")

    return "\n".join(lines)


# ─────────────────────────────────────────
# Print report to terminal (for testing)
# ─────────────────────────────────────────
def print_report(results):
    print(format_full_report(results))