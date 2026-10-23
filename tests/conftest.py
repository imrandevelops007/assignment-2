"""Shared pytest fixtures for the Assignment 2 test suite.

Add reusable fixtures here as needed (e.g., a stub/mock notifier used by
your test-doubles tests in Section 6).
"""

# TODO: implement your fixtures here.


from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_notifier():
    """A plain Mock standing in for the notifier collaborator (Section 6a).

    enroll_student() only calls notifier.send_confirmation(fee) or
    notifier.send_rejection(). A Mock accepts any method call and records it,
    so tests can check the return value (state verification) and which
    methods were called with which arguments (behavior verification) without
    sending a real email or notification. A fresh Mock is created for every
    test, so recorded calls never leak between tests.
    """
    return Mock()
