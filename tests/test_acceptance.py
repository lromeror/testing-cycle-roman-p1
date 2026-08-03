"""Part 5 - acceptance level.

These tests are functional: they are derived from SPECIFICATION.md, never from
the source code.  Each one implements one of the three Given / When / Then
criteria written in REPORT.md.

AC-1  Subtractive notation is mandatory          (specification section 2)
AC-2  Surrounding whitespace is trimmed          (specification section 3)
AC-3  Only canonical numerals are accepted       (specification sections 4 and 6)
"""

import pytest

from roman.converter import RomanError, add_roman, from_roman, is_valid_roman, to_roman


# ---------------------------------------------------------------------------
# AC-1
#   Given a user who converts a quantity to a roman numeral,
#   When the quantity contains a digit 4 or 9 in any position,
#   Then the system returns the subtractive form and never four identical
#        symbols in a row.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("quantity", "numeral"),
    [
        (1, "I"),
        (4, "IV"),
        (9, "IX"),
        (14, "XIV"),
        (40, "XL"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ],
)
def test_ac1_mandatory_reference_values(quantity, numeral):
    """Section 2, table of mandatory reference values."""
    assert to_roman(quantity) == numeral


@pytest.mark.parametrize(
    ("quantity", "forbidden"),
    [(4, "IIII"), (9, "VIIII"), (40, "XXXX"), (90, "LXXXX"), (400, "CCCC"), (900, "DCCCC")],
)
def test_ac1_the_incorrect_column_is_never_produced(quantity, forbidden):
    """Section 2, the 'Incorrect' column of the subtractive notation table."""
    assert to_roman(quantity) != forbidden


# ---------------------------------------------------------------------------
# AC-2
#   Given a numeral typed into a user facing field,
#   When it arrives with blanks before or after the symbols,
#   Then the system trims the ends and converts it, while a numeral with a
#        blank in the middle, or made of blanks only, is rejected.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("text", "value"), [("  IV  ", 4), ("X ", 10), (" mcmxciv", 1994), ("\tIX\n", 9)])
def test_ac2_surrounding_blanks_are_trimmed(text, value):
    """Section 3: leading and trailing whitespace is tolerated."""
    assert from_roman(text) == value


@pytest.mark.parametrize("text", ["X I", "M CM", "I V"])
def test_ac2_internal_blanks_are_rejected(text):
    """Section 3: internal whitespace is not tolerated."""
    with pytest.raises(RomanError):
        from_roman(text)


@pytest.mark.parametrize("text", ["", "   ", "\t", "\n  "])
def test_ac2_a_string_of_blanks_only_is_rejected(text):
    """Section 3: an empty string, or a string of blanks only, is invalid."""
    with pytest.raises(RomanError):
        from_roman(text)


def test_ac2_is_valid_roman_trims_as_well():
    """Section 6, table: "  IV  " is valid because the ends are trimmed."""
    assert is_valid_roman("  IV  ") is True


# ---------------------------------------------------------------------------
# AC-3
#   Given a numeral that represents a value but is not written in canonical
#        form,
#   When the system is asked to convert or validate it,
#   Then it is rejected: from_roman raises RomanError and is_valid_roman
#        returns False without raising.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("IIII", "the canonical form of 4 is IV"),
        ("VIIII", "the canonical form of 9 is IX"),
        ("XXXX", "the canonical form of 40 is XL"),
        ("VV", "the canonical form of 10 is X"),
        ("IVI", "4 + 1 = 5 is written V, rule 5"),
        ("IIIII", "I appears at most three times in a row, rule 1"),
        ("LL", "L appears at most once, rule 2"),
        ("IXIV", "after IX every group must be worth less than I, rule 5"),
    ],
)
def test_ac3_non_canonical_numerals_are_rejected(text, reason):
    """Section 4, normative table and the five formal rules."""
    with pytest.raises(RomanError):
        from_roman(text)


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IVI"])
def test_ac3_is_valid_roman_returns_false_without_raising(text):
    """Section 6: is_valid_roman never raises, it returns False."""
    assert is_valid_roman(text) is False


@pytest.mark.parametrize(("text", "value"), [("IV", 4), ("MCMXCIV", 1994), ("XIX", 19), ("XXXIX", 39)])
def test_ac3_canonical_numerals_are_still_accepted(text, value):
    """Section 4: the canonical rows of the table keep their value."""
    assert from_roman(text) == value


def test_ac3_arithmetic_only_ever_yields_canonical_results():
    """Section 7: the result of add_roman is always accepted by is_valid_roman."""
    assert is_valid_roman(add_roman("II", "II")) is True
