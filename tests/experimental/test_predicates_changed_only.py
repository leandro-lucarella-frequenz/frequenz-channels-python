# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the ChangedOnly implementation.

Most testing is done in the OnlyIfPrevious tests, these tests are limited to the
specifics of the ChangedOnly implementation.
"""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from frequenz.channels.experimental import ChangedOnly, OnlyIfPrevious


@dataclass(frozen=True, kw_only=True)
class EqualityTestCase:
    """Test case for testing ChangedOnly behavior with tricky equality cases."""

    title: str
    first_value: object
    second_value: object
    expected_second_result: bool


EQUALITY_TEST_CASES = [
    # Python's equality weirdness cases
    EqualityTestCase(
        title="Integer equals float",
        first_value=1,
        second_value=1.0,
        expected_second_result=False,
    ),
    EqualityTestCase(
        title="Boolean equals integer",
        first_value=True,
        second_value=1,
        expected_second_result=False,
    ),
    EqualityTestCase(
        title="Boolean equals float",
        first_value=True,
        second_value=1.0,
        expected_second_result=False,
    ),
    EqualityTestCase(
        title="False equals zero",
        first_value=False,
        second_value=0,
        expected_second_result=False,
    ),
    EqualityTestCase(
        title="Zero equals False",
        first_value=0,
        second_value=False,
        expected_second_result=False,
    ),
    # Edge cases that should be different
    EqualityTestCase(
        title="NaN is never equal to NaN",
        first_value=float("nan"),
        second_value=float("nan"),
        expected_second_result=True,
    ),
    EqualityTestCase(
        title="Different list instances with same content",
        first_value=[1],
        second_value=[1],
        expected_second_result=False,
    ),
]


def test_changed_only_inheritance() -> None:
    """Test that ChangedOnly is properly inheriting from OnlyIfPrevious."""
    changed_only = ChangedOnly()
    assert isinstance(changed_only, OnlyIfPrevious)


def test_changed_only_predicate_implementation() -> None:
    """Test that ChangedOnly properly implements the inequality predicate."""
    # Create mock objects that we can control the equality comparison for
    old = MagicMock()
    new = MagicMock()

    # Set up the inequality comparison
    # mypy doesn't understand mocking __ne__ very well
    old.__ne__.return_value = True  # type: ignore[attr-defined]

    changed_only = ChangedOnly()
    # Skip the first message as it's handled by first_is_true
    changed_only(old)
    changed_only(new)

    # Verify that __ne__ was called with the correct argument
    old.__ne__.assert_called_once_with(new)  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "test_case",
    EQUALITY_TEST_CASES,
    ids=lambda test_case: test_case.title,
)
def test_changed_only_equality_cases(test_case: EqualityTestCase) -> None:
    """Test ChangedOnly behavior with Python's tricky equality cases.

    Args:
        test_case: The test case containing the input values and expected result.
    """
    changed_only = ChangedOnly()
    assert changed_only(test_case.first_value) is True  # First is always True
    assert changed_only(test_case.second_value) is test_case.expected_second_result


def test_changed_only_representation() -> None:
    """Test the string representation of ChangedOnly."""
    changed_only = ChangedOnly()
    assert str(changed_only) == "ChangedOnly"
    assert repr(changed_only) == "ChangedOnly(first_is_true=True)"
