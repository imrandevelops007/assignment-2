"""Test suite for src/registration.py (Assignment 2).

This file is intentionally left for you to implement. See the assignment
handout for the required work:

  - Section 4: Statement and branch coverage (summarize_batch_registrations,
    enroll_student) -- close every gap your coverage report shows.
  - Section 5: Data-flow testing (defs/uses/DU pairs for `total_fees` in
    summarize_batch_registrations; All-Uses coverage).
  - Section 6: Test doubles (stub/mock notifier for enroll_student).

`registration` is importable directly (see pyproject.toml's `pythonpath`
setting), e.g.:

    from registration import (
        can_register,
        calculate_registration_fee,
        summarize_batch_registrations,
        enroll_student,
    )
"""

# TODO: implement your tests here.



import pytest

from registration import enroll_student, summarize_batch_registrations

pytestmark = pytest.mark.unit



# Section 4 - Coverage of summarize_batch_registrations


@pytest.mark.positive
def test_batch_with_one_approved_request_counts_it_and_sums_its_fee():
    # 9 + 3 = 12 credits -> 12 * $100 = $1,200
    assert summarize_batch_registrations([(9, 3, True)]) == (1, 1200.0)



# Section 4 - Coverage of enroll_student


@pytest.mark.positive
def test_enroll_student_returns_true_when_registration_allowed(mock_notifier):
    # Section 6(b). 9 + 3 = 12 credits -> fee $1,200.
    result = enroll_student(9, 3, True, mock_notifier)

    # State verification: the function's own result.
    assert result is True

    # Behavior verification: how it talked to the collaborator.
    mock_notifier.send_confirmation.assert_called_once_with(1200.0)
    mock_notifier.send_rejection.assert_not_called()


@pytest.mark.negative
def test_enroll_student_returns_false_when_prerequisite_not_met(mock_notifier):
    # Section 6(c). Prerequisite missing -> registration rejected.
    result = enroll_student(9, 3, False, mock_notifier)

    # State verification
    assert result is False

    # Behavior verification: rejection sent once, with no arguments; no fee sent.
    mock_notifier.send_rejection.assert_called_once_with()
    mock_notifier.send_confirmation.assert_not_called()





@pytest.mark.negative
def test_batch_skips_rejected_request_without_counting_or_charging_it():
    requests = [(9, 3, True), (9, 3, False)]
    assert summarize_batch_registrations(requests) == (1, 1200.0)


@pytest.mark.boundary
def test_empty_batch_returns_zero_count_and_zero_fees():
    assert summarize_batch_registrations([]) == (0, 0.0)





# Section 5 - Data-flow testing of total_fees


@pytest.mark.negative
def test_batch_with_only_rejected_requests_returns_zero_count_and_zero_fees():
    requests = [(9, 3, False), (16, 1, True)]   # prerequisite missing; current > 15
    assert summarize_batch_registrations(requests) == (0, 0.0)


@pytest.mark.positive
def test_batch_total_fees_accumulates_across_multiple_approved_requests():
    requests = [
        (9, 3, True),    # 12 credits -> $1,200
        (10, 4, True),   # 14 credits -> $1,200 + 2 * $75 = $1,350
    ]
    assert summarize_batch_registrations(requests) == (2, 2550.0)