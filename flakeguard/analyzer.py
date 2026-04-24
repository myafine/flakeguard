"""
analyzer.py — Core Static Analyzer

Reads a Python test file, parses it into an AST,
walks every node, and returns a list of flakiness warnings.
"""

import ast
from flakeguard.patterns import ALL_PATTERNS


# ─────────────────────────────────────────
# Data structure for a single warning
# ─────────────────────────────────────────
class Warning:
    def __init__(self, test_name, line, message):
        self.test_name = test_name  # name of the test function
        self.line = line            # line number in the file
        self.message = message      # human-readable warning

    def __repr__(self):
        return f"[Line {self.line}] {self.test_name}: {self.message}"


# ─────────────────────────────────────────
# Find which test function a node belongs to
# ─────────────────────────────────────────
def get_parent_test(node, test_functions):
    """
    Given a node and a list of test function definitions,
    return the name of the test that contains this node.
    """
    for func in test_functions:
        if func.lineno <= node.lineno <= func.end_lineno:
            return func.name
    return "unknown"


# ─────────────────────────────────────────
# Main analysis function
# ─────────────────────────────────────────
def analyze_file(filepath):
    """
    Analyze a single Python test file.

    Returns a list of Warning objects, one per detected issue.
    """
    warnings = []

    # Step 1: Read the file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []

    # Step 2: Parse into AST
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []

    # Step 3: Find all test functions (functions starting with "test_")
    test_functions = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith("test_")
    ]

    if not test_functions:
        print(f"No test functions found in {filepath}")
        return []

    # Step 4: Walk every node in the tree
    for node in ast.walk(tree):

        # Only check nodes that are inside a test function
        if not hasattr(node, "lineno"):
            continue

        parent_test = get_parent_test(node, test_functions)
        if parent_test == "unknown":
            continue

        # Step 5: Run every pattern on this node
        for pattern in ALL_PATTERNS:
            result = pattern(node)
            if result:
                warnings.append(Warning(
                    test_name=parent_test,
                    line=node.lineno,
                    message=result
                ))

    return warnings


# ─────────────────────────────────────────
# Analyze multiple files at once
# ─────────────────────────────────────────
def analyze_files(filepaths):
    """
    Analyze a list of test files.
    Returns a dict: { filepath: [Warning, ...] }
    """
    results = {}
    for filepath in filepaths:
        warnings = analyze_file(filepath)
        if warnings:
            results[filepath] = warnings
    return results