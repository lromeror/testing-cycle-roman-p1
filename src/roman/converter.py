class RomanError(ValueError):
    pass


_PAIRS = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


_SINGLE = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


_VALID_SUBTRACTIVE = {"IV", "IX", "XL", "XC", "CD", "CM"}


_MIN_VALUE = 1
_MAX_VALUE = 3999


def to_roman(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise RomanError("value must be an integer")
    if n < _MIN_VALUE:
        raise RomanError("value must be >= 1")
    if n > _MAX_VALUE:
        raise RomanError("value must be <= 3999")
    out = []
    remaining = n
    for value, symbol in _PAIRS:
        while remaining >= value:
            out.append(symbol)
            remaining -= value
    return "".join(out)


def _split_groups(text):
    """Read `text` as the sequence of groups of specification section 4.

    A group is one of the six subtractive pairs or a single symbol.  Rule 3
    also forbids any other symbol followed by one of greater value.
    """
    groups = []
    i = 0
    length = len(text)
    while i < length:
        if i + 1 < length and text[i:i + 2] in _VALID_SUBTRACTIVE:
            groups.append(text[i:i + 2])
            i += 2
            continue
        if i + 1 < length and _SINGLE[text[i]] < _SINGLE[text[i + 1]]:
            raise RomanError("invalid subtractive pair: " + text[i:i + 2])
        groups.append(text[i])
        i += 1
    return groups


def _group_value(group):
    if len(group) == 2:
        return _SINGLE[group[1]] - _SINGLE[group[0]]
    return _SINGLE[group]


def _check_canonical(text, groups):
    """Apply the five formal rules of specification section 4."""
    for symbol in "IXCM":
        if symbol * 4 in text:
            raise RomanError(symbol + " may appear at most three times in a row")
    for symbol in "VLD":
        if _count_char(text, symbol) > 1:
            raise RomanError(symbol + " may appear at most once")
    for pair in _VALID_SUBTRACTIVE:
        if groups.count(pair) > 1:
            raise RomanError("subtractive pair " + pair + " may appear at most once")
    previous = None
    limit = None
    for group in groups:
        value = _group_value(group)
        if previous is not None and value > previous:
            raise RomanError("group values must not increase: " + text)
        if limit is not None and value >= limit:
            raise RomanError("group after a subtractive pair is too large: " + text)
        if len(group) == 2:
            limit = _SINGLE[group[0]]
        previous = value


def from_roman(s):
    if not isinstance(s, str):
        raise RomanError("value must be a string")
    text = s.upper()
    if text == "":
        raise RomanError("empty string is not a roman numeral")
    for ch in text:
        if ch not in _SINGLE:
            raise RomanError("invalid roman character: " + ch)
    groups = _split_groups(text)
    _check_canonical(text, groups)
    total = 0
    for group in groups:
        total += _group_value(group)
    if total < _MIN_VALUE or total > _MAX_VALUE:
        raise RomanError("value out of range 1..3999")
    return total


def _count_char(text, ch):
    total = 0
    for c in text:
        if c == ch:
            total += 1
    return total


def is_valid_roman(s):
    try:
        from_roman(s)
        return True
    except RomanError:
        return False


def add_roman(a, b):
    return to_roman(from_roman(a) + from_roman(b))


def subtract_roman(a, b):
    return to_roman(from_roman(a) - from_roman(b))
