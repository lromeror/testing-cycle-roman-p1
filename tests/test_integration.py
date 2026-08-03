"""Part 4 - integration level.

Unit tests exercise one function at a time.  These tests combine two or more
units and verify that they work together as a group, as required by section 7
of SPECIFICATION.md:

    add_roman and subtract_roman are built on top of from_roman and to_roman,
    and their result must be accepted by is_valid_roman.

The collaborations under test are:

    add_roman      -> from_roman + to_roman -> is_valid_roman
    subtract_roman -> from_roman + to_roman -> is_valid_roman
    is_valid_roman -> from_roman
"""

import pytest

from roman.converter import (
    RomanError,
    add_roman,
    from_roman,
    is_valid_roman,
    subtract_roman,
    to_roman,
)


# ---------------------------------------------------------------------------
# The output of to_roman is fed to is_valid_roman through add_roman.
# ---------------------------------------------------------------------------


def test_add_roman_result_is_accepted_by_is_valid_roman():
    """Section 7: the result of add_roman is always accepted by is_valid_roman.

    Neither unit detects this on its own: from_roman("II") is 2, to_roman
    passes its own inherited tests, and is_valid_roman("IV") is True.  Only the
    composition puts the output of to_roman in front of is_valid_roman.
    """
    result = add_roman("II", "II")
    assert is_valid_roman(result), f"add_roman produced a non canonical string: {result!r}"
    assert result == "IV"


def test_subtract_roman_result_is_accepted_by_is_valid_roman():
    """Section 7, same collaboration through subtract_roman."""
    result = subtract_roman("VI", "II")
    assert is_valid_roman(result), f"subtract_roman produced a non canonical string: {result!r}"
    assert result == "IV"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ("II", "II", "IV"),
        ("IV", "VI", "X"),
        ("MCMXCIV", "VI", "MM"),
        ("III", "I", "IV"),
        ("XXXV", "V", "XL"),
    ],
)
def test_add_roman_agrees_with_the_conversion_pair(a, b, expected):
    """add_roman(a, b) must equal to_roman(from_roman(a) + from_roman(b))."""
    assert add_roman(a, b) == expected
    assert from_roman(add_roman(a, b)) == from_roman(a) + from_roman(b)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [("X", "I", "IX"), ("L", "X", "XL"), ("M", "C", "CM"), ("V", "I", "IV")],
)
def test_subtract_roman_agrees_with_the_conversion_pair(a, b, expected):
    """subtract_roman(a, b) must equal to_roman(from_roman(a) - from_roman(b))."""
    assert subtract_roman(a, b) == expected
    assert from_roman(subtract_roman(a, b)) == from_roman(a) - from_roman(b)


# ---------------------------------------------------------------------------
# Range errors must cross the whole collaboration as RomanError, section 7.
# ---------------------------------------------------------------------------


def test_subtract_below_the_range_raises():
    """Section 7: subtract_roman("I", "I") is 0, outside the range."""
    with pytest.raises(RomanError):
        subtract_roman("I", "I")


def test_add_above_the_range_raises():
    """Section 7: add_roman("MMM", "M") is 4000, outside the range."""
    with pytest.raises(RomanError):
        add_roman("MMM", "M")


def test_invalid_operand_propagates_as_roman_error():
    """A defect in one operand must not escape as another exception type."""
    with pytest.raises(RomanError):
        add_roman("IIII", "I")
    with pytest.raises(RomanError):
        add_roman("Z", "I")


# ---------------------------------------------------------------------------
# is_valid_roman delegates to from_roman: the two must agree.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["IV", "MCMXCIV", "III", "MMMCMXCIX"])
def test_is_valid_roman_agrees_with_from_roman_on_valid_input(text):
    assert is_valid_roman(text) is True
    assert from_roman(text) == from_roman(text)


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IL", "MMMM", "Z", ""])
def test_is_valid_roman_agrees_with_from_roman_on_invalid_input(text):
    """Section 6: is_valid_roman is False exactly when from_roman raises."""
    assert is_valid_roman(text) is False
    with pytest.raises(RomanError):
        from_roman(text)


# ---------------------------------------------------------------------------
# Full round trip across to_roman and from_roman.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 4, 9, 14, 40, 90, 400, 900, 1994, 2024, 3999])
def test_round_trip_is_the_identity(n):
    assert from_roman(to_roman(n)) == n


@pytest.mark.parametrize("n", [1, 4, 9, 44, 99, 444, 999, 1994, 3888, 3999])
def test_every_conversion_output_is_valid(n):
    """to_roman must only ever produce strings that is_valid_roman accepts."""
    assert is_valid_roman(to_roman(n))
