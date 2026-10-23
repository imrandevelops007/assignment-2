# Assignment 2 — Coverage, Data-Flow Testing, and Test Doubles (Starter Code)

This is the starter code for SE 413/513 Assignment 2. `src/registration.py`
is complete and **must not be modified** — it includes the two functions
from Assignment 1 (`can_register`, `calculate_registration_fee`, unchanged)
plus two new functions this assignment targets:

- `summarize_batch_registrations(requests)` — processes a batch of
  registration requests and accumulates an approval count and total fees.
- `enroll_student(current_credits, course_credits, prerequisite_met, notifier)`
  — attempts to enroll a student and notifies the result through a
  `notifier` collaborator (`send_confirmation(fee)` / `send_rejection()`).

## Project layout

```
assignment-2/
|-- src/registration.py        (provided — do not modify)
|-- tests/test_registration.py (implement your tests here)
|-- tests/conftest.py          (implement your fixtures here)
|-- pyproject.toml
|-- README.md
```

## Setup

1. (Recommended) Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```
   pip install pytest pytest-cov
   ```

## Running the tests

From the project root:

```
pytest
```

## Measuring coverage

`pyproject.toml` already configures branch measurement and restricts
coverage to `src/` (see `[tool.coverage.run]`). Run:

```
pytest --cov --cov-branch --cov-report=term-missing
```

This reports statement and branch coverage together, with a `Missing`
column listing uncovered lines and `a->b` arcs (uncovered branch
outcomes). Add tests until no gaps remain for
`summarize_batch_registrations` and `enroll_student` (Section 4 of the
assignment). Because the report measures the whole file, it may also list
lines inside `can_register`/`calculate_registration_fee` (lines 15-59) —
those were already covered in Assignment 1 and are **not** part of this
assignment's coverage target; only close gaps inside
`summarize_batch_registrations` and `enroll_student` (lines 62 onward).

To see statement-only coverage for comparison (Section 4c), drop
`--cov-branch`:

```
pytest --cov --cov-report=term-missing
```

## Notes

- Do not modify `src/registration.py`. If you believe there is a defect in
  it, contact the instructor rather than changing it yourself.
- `registration` is importable directly in your tests (no `src.` prefix
  needed), e.g. `from registration import can_register`.
- The four markers from Assignment 1 (`unit`, `positive`, `negative`,
  `boundary`) are already registered in `pyproject.toml` if you find them
  useful here; this assignment does not require new markers.



---

## Section 4: Statement and Branch Coverage

**Scope.** Only `summarize_batch_registrations` (lines 62–89) and `enroll_student`
(lines 92–117) are targets. The report measures the whole file, so it still lists
lines 25, 28, 31, 50 and 57–59. Those are inside `can_register` and
`calculate_registration_fee` (lines 15–59), which the handout excludes from this
assignment's coverage target.

**Why a separate config for statement-only coverage.** `pyproject.toml` sets
`branch = true` under `[tool.coverage.run]`, so dropping `--cov-branch` still
measures branches. `.coveragerc-statements` is identical except for
`branch = False`, which gives a true statement-only report.
`src/registration.py` is not changed.

### 4(a) Statement coverage

How the gaps were closed:

1. With one approved batch and one allowed enrollment, the report listed **116–117**
   (the rejection path of `enroll_student`) as missing.
2. Adding `test_enroll_student_returns_false_when_prerequisite_not_met` covered
   them, leaving **0 missing statements** in both target functions.

Final statement-only report:

```
(.venv) PS E:\assignment-2> pytest --cov --cov-report=term-missing --cov-config=.coveragerc-statements
Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
src\registration.py      36      7    81%   25, 28, 31, 50, 57-59
---------------------------------------------------
TOTAL                    36      7    81%
```

No line from 62 onward appears under Missing.

### 4(b) Branch coverage

With full statement coverage, the branch report still showed the arc **`84->83`**:
the `if` inside the loop had never been False, so no request had ever been rejected
and skipped. Every *line* had run, but one *decision outcome* had not. Adding
`test_batch_skips_rejected_request_without_counting_or_charging_it` closed it.

Final branch-coverage report:

```
(.venv) PS E:\assignment-2> pytest --cov --cov-branch --cov-report=term-missing
Name                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------
src\registration.py      36      7     18      5    78%   25, 28, 31, 50, 57-59
-----------------------------------------------------------------
TOTAL                    36      7     18      5    78%
```

No line or `a->b` arc from 62 onward appears under Missing. The 5 remaining
partial branches are all inside `can_register` / `calculate_registration_fee`.

### Which tests exercise each decision outcome

| Decision | Outcome (arc) | Exercised by |
|---|---|---|
| `for` loop, line 83 | enters the body (83→84) | `test_batch_with_one_approved_request_counts_it_and_sums_its_fee`, since its batch has one request |
| | exits the loop (83→89) | every batch test, when the loop finishes; `test_empty_batch_returns_zero_count_and_zero_fees` takes this exit immediately with zero iterations |
| `if can_register(...)`, line 84 | True (84→85) | `test_batch_with_one_approved_request_counts_it_and_sums_its_fee`, since (9, 3, True) is approved and counted |
| | False (84→83) | `test_batch_skips_rejected_request_without_counting_or_charging_it`, since (9, 3, False) is rejected and the loop moves on |
| `if can_register(...)`, line 110 | True (110→111) | `test_enroll_student_returns_true_when_registration_allowed`, since (9, 3, True) is enrolled |
| | False (110→116) | `test_enroll_student_returns_false_when_prerequisite_not_met`, since (9, 3, False) is rejected |



---

## Section 5: Data-Flow Testing of `total_fees`

Notation follows the Week 6 lecture (`sum_positive()` example): D = definition,
c-use = value read in a computation or output, p-use = value read in a predicate.

### 5(a) Definitions and uses

| ID | Line | Statement | Event |
|---|---|---|---|
| D1 | 81 | `total_fees = 0.0` | definition (initialization before the loop) |
| U1 | 87 | `total_fees = total_fees + calculate_registration_fee(total_credits)` | **c-use**: the old value is read on the right-hand side |
| D2 | 87 | (same statement) | **definition**: the new sum is stored |
| U2 | 89 | `return approved_count, total_fees` | **c-use**: the value is returned |

Line 87 contains both a use and a definition: the old value of `total_fees` is
read first, then a new value is written. `total_fees` has **no p-uses**: it is
never read in a predicate. The `if` on line 84 decides *whether* line 87 runs,
but it does not read `total_fees`.

### 5(b) DU-pair table

| # | Def | Use | When the def-clear path exists | Exercised by |
|---|---|---|---|---|
| 1 | D1 (81) | U1 (87) | the first approved request in the batch reads the initial 0.0 | `test_batch_with_one_approved_request_counts_it_and_sums_its_fee` |
| 2 | D1 (81) | U2 (89) | line 87 never runs: an empty batch, or every request rejected | `test_empty_batch_returns_zero_count_and_zero_fees`, `test_batch_with_only_rejected_requests_returns_zero_count_and_zero_fees` |
| 3 | D2 (87) | U1 (87) | **loop-carried**: a later approved request reads the total written by an earlier one | `test_batch_total_fees_accumulates_across_multiple_approved_requests` |
| 4 | D2 (87) | U2 (89) | at least one request is approved, then the loop exits | `test_batch_with_one_approved_request_counts_it_and_sums_its_fee`, `test_batch_skips_rejected_request_without_counting_or_charging_it` (here D2 also survives a skipped, rejected iteration before reaching the return) |

All four pairs are exercised, so the suite satisfies **All-Uses** for `total_fees`.

### 5(c) The loop-carried pair (#3)

`test_batch_total_fees_accumulates_across_multiple_approved_requests` submits two
approved requests ($1,200 and $1,350) and asserts `total_fees == 2550.0`. On the
second approval, line 87 reads the value that line 87 itself wrote on the first
approval, so the def D2 reaches the use U1 across a loop iteration.

**Why zero or one approved request cannot exercise this pair:** with zero
approvals, line 87 never runs, so D2 never happens. With exactly one approval,
line 87 runs once and reads D1 (0.0), and the D2 it writes is read only by the
`return`, never by a second execution of line 87. A suite with one approved batch
plus an empty batch already satisfies **All-Defs** (D1 and D2 each reach at least
one use), so All-Defs would accept it without ever testing accumulation. Only
**All-Uses**, which requires every DU pair, forces the two-approval test.

**Why this matters:** if line 87 were mistakenly written as
`total_fees = 0.0 + calculate_registration_fee(total_credits)`, every other test
in the suite would still pass, and statement and branch coverage would still be
100%. Only this test would fail, returning 1350.0 instead of 2550.0.