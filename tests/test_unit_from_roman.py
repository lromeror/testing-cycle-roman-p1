"""Part 3 - unit level, structural tests for from_roman and is_valid_roman.

These tests complete the branch coverage of src/roman/converter.py: every
guard of `from_roman` (lines 56-84) and both exits of `is_valid_roman`
(lines 99-104).  As above, the inputs come from the code and the expected
results come from SPECIFICATION.md.
"""

import pytest

from roman.converter import RomanError, add_roman, from_roman, is_valid_roman, subtract_roman


# ---------------------------------------------------------------------------
# from_roman: the guards, one test per branch.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [123, None, ["I"], 4.0])
def test_non_string_raises(value):
    """Line 57: `not isinstance(s, str)` True. Specification section 3."""
    with pytest.raises(RomanError):
        from_roman(value)


def test_empty_string_raises():
    """Line 60: the empty string guard. Specification section 3."""
    with pytest.raises(RomanError):
        from_roman("")


@pytest.mark.parametrize("value", ["Z", "IZ", "1", "I,V"])
def test_character_outside_the_alphabet_raises(value):
    """Line 63: `ch not in _SINGLE` True. Specification section 3."""
    with pytest.raises(RomanError):
        from_roman(value)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("IV", 4), ("IX", 9), ("XL", 40), ("XC", 90), ("CD", 400), ("CM", 900)],
)
def test_the_six_valid_subtractive_pairs(text, expected):
    """Lines 71-74: `pair in _VALID_SUBTRACTIVE` True. Specification section 2."""
    assert from_roman(text) == expected


@pytest.mark.parametrize("text", ["IL", "IC", "VX", "IM", "XM"])
def test_invalid_subtractive_pair_raises(text):
    """Line 78-79: `current < nxt` outside the six pairs. Specification section 5."""
    with pytest.raises(RomanError):
        from_roman(text)


def test_value_above_the_range_raises():
    """Specification section 3: "MMMM", which is 4000, is invalid.

    After the canonical form fix it is rule 1 of section 4 that rejects it, four
    M in a row, and no longer the range guard.  The observable result required
    by the specification, a RomanError, is the same.
    """
    with pytest.raises(RomanError):
        from_roman("MMMM")


def test_lower_case_is_accepted():
    """Line 59: `s.upper()`. Specification section 3."""
    assert from_roman("mcmxciv") == 1994


def test_last_symbol_without_a_successor():
    """Lines 69 and 76: `i + 1 < length` False on the final symbol."""
    assert from_roman("MI") == 1001


# ---------------------------------------------------------------------------
# Canonical form.  Specification section 4: a string that represents a value
# but is not the canonical form of that value is rejected.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "LL", "DD", "IVI", "IXI"])
def test_non_canonical_forms_are_rejected(text):
    """Specification section 4, normative table and the five formal rules."""
    with pytest.raises(RomanError):
        from_roman(text)


@pytest.mark.parametrize("text", ["IXIX", "XCXC", "CMCM"])
def test_rule_3_a_subtractive_pair_may_appear_at_most_once(text):
    """Section 4, rule 3: each of the six pairs at most once in the string."""
    with pytest.raises(RomanError):
        from_roman(text)


@pytest.mark.parametrize("text", ["XCM", "IXC", "IVX", "XLM"])
def test_rule_4_group_values_must_not_increase(text):
    """Section 4, rule 4: group values are non increasing from left to right."""
    with pytest.raises(RomanError):
        from_roman(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("IV", 4), ("MCMXCIV", 1994), ("MMMCMXCIX", 3999), ("XIV", 14), ("III", 3)],
)
def test_canonical_forms_are_accepted(text, expected):
    """Specification section 4: canonical strings keep working."""
    assert from_roman(text) == expected


# ---------------------------------------------------------------------------
# is_valid_roman: both exits, and the promise that it never raises.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["IV", "MCMXCIV", "iv"])
def test_is_valid_roman_true_branch(value):
    """Line 102: `return True`."""
    assert is_valid_roman(value) is True


@pytest.mark.parametrize("value", ["IIII", "Z", "", "MMMM", "IL"])
def test_is_valid_roman_false_branch(value):
    """Lines 103-104: the except branch. Specification section 6."""
    assert is_valid_roman(value) is False


@pytest.mark.parametrize("value", [123, None, 4.0, ["I"], object()])
def test_is_valid_roman_never_raises(value):
    """Specification section 6: it never raises, for any type of input."""
    assert is_valid_roman(value) is False


# ---------------------------------------------------------------------------
# add_roman and subtract_roman: lines 108 and 112, unit level only.
# ---------------------------------------------------------------------------


def test_add_roman_returns_a_roman_string():
    """Line 108. Specification section 7."""
    assert add_roman("IV", "VI") == "X"


def test_subtract_roman_returns_a_roman_string():
    """Line 112. Specification section 7."""
    assert subtract_roman("X", "I") == "IX"
