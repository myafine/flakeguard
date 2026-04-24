"""
patterns.py — Flakiness Pattern Definitions

Each pattern is a function that receives an AST node and returns
a warning message if a flakiness signal is detected, or None if clean.
"""

import ast


# ─────────────────────────────────────────
# PATTERN 1: Sleeping inside a test
# Signals: time-dependent behavior
# Example: time.sleep(2) or sleep(1)
# ─────────────────────────────────────────
def check_sleep(node):
    if not isinstance(node, ast.Call):
        return None

    # Matches: time.sleep(...)
    if (isinstance(node.func, ast.Attribute) and
            node.func.attr == "sleep"):
        return ("⏱ time.sleep() detected. Tests that wait for a fixed "
                "duration are sensitive to system load and often flaky. "
                "Consider using an event-driven wait or mock instead.")

    # Matches: sleep(...) directly
    if (isinstance(node.func, ast.Name) and
            node.func.id == "sleep"):
        return ("⏱ sleep() detected. Tests that wait for a fixed "
                "duration are sensitive to system load and often flaky. "
                "Consider using an event-driven wait or mock instead.")

    return None


# ─────────────────────────────────────────
# PATTERN 2: Network calls inside a test
# Signals: external dependency, non-determinism
# Example: requests.get(...), urllib.request.urlopen(...)
# ─────────────────────────────────────────
NETWORK_CALLS = {
    "requests": ["get", "post", "put", "delete", "patch", "head"],
    "urllib":   ["urlopen", "urlretrieve"],
    "http":     ["request"],
    "socket":   ["connect", "create_connection"],
}

def check_network(node):
    if not isinstance(node, ast.Call):
        return None

    if isinstance(node.func, ast.Attribute):
        method = node.func.attr

        # Get the root object name (e.g. "requests" in requests.get)
        root = node.func.value
        if isinstance(root, ast.Name):
            module = root.id
            if module in NETWORK_CALLS and method in NETWORK_CALLS[module]:
                return (f"🌐 Network call detected ({module}.{method}). "
                        "Tests that make real network requests are unreliable "
                        "in CI environments. Use mocking (unittest.mock) instead.")

    return None


# ─────────────────────────────────────────
# PATTERN 3: Use of randomness
# Signals: non-deterministic output
# Example: random.random(), random.choice()
# ─────────────────────────────────────────
RANDOM_CALLS = ["random", "randint", "choice", "shuffle", "sample", "uniform"]

def check_randomness(node):
    if not isinstance(node, ast.Call):
        return None

    if isinstance(node.func, ast.Attribute):
        if (isinstance(node.func.value, ast.Name) and
                node.func.value.id == "random" and
                node.func.attr in RANDOM_CALLS):
            return (f"🎲 Random call detected (random.{node.func.attr}). "
                    "Tests using randomness without a fixed seed produce "
                    "different results on each run. Set a seed with "
                    "random.seed() or use fixed test data.")

    return None


# ─────────────────────────────────────────
# PATTERN 4: Hardcoded dates / time.time()
# Signals: time-dependent assertions
# Example: datetime.now(), time.time()
# ─────────────────────────────────────────
TIME_CALLS = ["now", "today", "time", "utcnow"]

def check_datetime(node):
    if not isinstance(node, ast.Call):
        return None

    if isinstance(node.func, ast.Attribute):
        if node.func.attr in TIME_CALLS:
            return (f"📅 Time-dependent call detected ({node.func.attr}). "
                    "Tests that depend on the current date/time will behave "
                    "differently depending on when they run. Use a fixed "
                    "datetime or mock time with freezegun.")

    return None


# ─────────────────────────────────────────
# PATTERN 5: Setting environment variables
# Signals: shared global state between tests
# Example: os.environ["KEY"] = "value"
# ─────────────────────────────────────────
def check_env_mutation(node):
    if not isinstance(node, ast.Assign):
        return None

    for target in node.targets:
        # Matches: os.environ["KEY"] = ...
        if (isinstance(target, ast.Subscript) and
                isinstance(target.value, ast.Attribute) and
                target.value.attr == "environ"):
            return ("🔧 Environment variable mutation detected (os.environ). "
                    "Modifying environment variables in tests can leak state "
                    "into other tests. Use monkeypatch or mock.patch.dict instead.")

    return None


# ─────────────────────────────────────────
# ALL PATTERNS — used by analyzer.py
# ─────────────────────────────────────────
ALL_PATTERNS = [
    check_sleep,
    check_network,
    check_randomness,
    check_datetime,
    check_env_mutation,
]