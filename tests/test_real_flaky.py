"""
A sample test file with flakiness issues — for testing our analyzer.
"""
import time
import requests
import random
import os


def test_login():
    time.sleep(2)  # ← flaky: timing dependency
    assert True


def test_fetch_user():
    response = requests.get("https://api.example.com/user")  # ← flaky: real network call
    assert response.status_code == 200


def test_random_id():
    user_id = random.randint(1, 1000)  # ← flaky: randomness
    assert user_id > 0


def test_set_env():
    os.environ["DEBUG"] = "true"  # ← flaky: env mutation
    assert os.environ["DEBUG"] == "true"


def test_clean():
    # This test has no flakiness signals — should produce no warnings
    result = 1 + 1
    assert result == 2