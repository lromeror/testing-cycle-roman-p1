"""Part 3 - unit level, structural tests for to_roman.

The test cases are derived from the source code of `to_roman`
(src/roman/converter.py, lines 40-53): one test per basis path of the control
flow graph, plus one test per definition-use pair.  Structural testing chooses
the *inputs*; the *expected results* still come from SPECIFICATION.md, which is
the oracle.  When the code and the specification disagree, the code has the
defect.

Node numbering matches the control flow graph in REPORT.md.
"""

import pytest

from roman.converter import RomanError, to_roman


# ---------------------------------------------------------------------------
# Basis path coverage.  V(G) = 7, so seven linearly independent paths.
# P5 and P6 are infeasible (see REPORT.md): _PAIRS is a non-empty constant and
# its last entry has value 1, so for n >= 1 the loop body always executes.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["X", 4.0, None, [4], 4 + 0j])
def test_p1_first_operand_true_non_integer_raises(value):
    """P1: N1-N2-N4-N14. `not isinstance(n, int)` is True, short circuit."""
    with pytest.raises(RomanError):
        to_roman(value)


@pytest.mark.parametrize("value", [True, False])
def test_p2_second_operand_true_bool_raises(value):
    """P2: N1-N2-N3-N4-N14. isinstance(n, int) is True but n is a bool.

    Specification section 1: `True` is not 1.
    """
    with pytest.raises(RomanError):
        to_roman(value)


@pytest.mark.parametrize("value", [0, -1, -3999])
def test_p3_below_lower_bound_raises(value):
    """P3: N1-N2-N3-N5-N6-N14. `n < _MIN_VALUE` is True."""
    with pytest.raises(RomanError):
        to_roman(value)


@pytest.mark.parametrize("value", [4000, 5000])
def test_p4_above_upper_bound_raises(value):
    """P4: N1-N2-N3-N5-N7-N8-N14. `n > _MAX_VALUE` is True."""
    with pytest.raises(RomanError):
        to_roman(value)


def test_p7_loop_body_executes_and_returns():
    """P7: N1-...-N9-N10-N11-N12-N11-N10-N13-N14. The only feasible loop path."""
    assert to_roman(1) == "I"


@pytest.mark.parametrize("value", [1, 3999])
def test_boundaries_of_the_valid_range_are_accepted(value):
    """N5 and N7 both False at the extremes of the range (section 1)."""
    assert to_roman(value) != ""


# ---------------------------------------------------------------------------
# Data flow coverage for `remaining`, which is defined at line 48 and
# redefined at line 52 inside the loop.
# ---------------------------------------------------------------------------


def test_du_def48_puse50_and_cuse52():
    """(48, 50) p-use and (48, 52) c-use, with no redefinition in between.

    n = 1 makes the predicate at line 50 False for every pair down to (5, 'V')
    and True for (1, 'I'), which is where the c-use at line 52 happens.
    """
    assert to_roman(1) == "I"


def test_du_def52_puse50_true_and_def52_cuse52():
    """(52, 50) p-use True and (52, 52) c-use: the same pair is applied twice.

    n = 3 re-enters the while body using the value that line 52 redefined.
    """
    assert to_roman(3) == "III"


def test_du_def52_puse50_false_terminates_the_loop():
    """(52, 50) p-use False: after the redefinition the predicate stops the loop."""
    assert to_roman(10) == "X"


def test_du_remaining_crosses_several_pairs():
    """The def at 52 reaches the p-use at 50 of later iterations of the for loop."""
    assert to_roman(1994) == "MCMXCIV"


# ---------------------------------------------------------------------------
# The (5, "IV") entry of _PAIRS.  Structurally, the p-use at line 50 can never
# distinguish it from the preceding (5, "V") entry, so the "IV" symbol is
# unreachable: line 51 never appends it.  Specification section 2 requires
# subtractive notation, so this is a defect of the code, not of the test.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (4, "IV"),
        (9, "IX"),
        (14, "XIV"),
        (40, "XL"),
        (90, "XC"),
        (400, "CD"),
        (900, "CM"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ],
)

def test_subtractive_notation_is_mandatory(number, expected):
    """Mandatory reference values of specification section 2."""
    assert to_roman(number) == expected


@pytest.mark.parametrize("number", [4, 9, 40, 90, 400, 900, 1994, 3999])
def test_never_four_identical_symbols_in_a_row(number):
    """Section 2: the system never produces four identical symbols in a row."""
    result = to_roman(number)
    for symbol in "IXCM":
        assert symbol * 4 not in result
