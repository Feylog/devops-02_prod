"""Base62 encoder/decoder for URL shortener short codes.

Pure functions, no I/O, no side effects. Encoding/decoding is the inverse
operation: decode(encode(n)) == n for any non-negative integer n.

Used to convert auto-increment database IDs to compact, URL-safe codes.
"""

# The 62-character alphabet: digits, then uppercase, then lowercase.
# Order matters — changing it would break previously-issued short codes.
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)  # 62


def encode(n: int) -> str:
    """Convert a non-negative integer to its base62 string representation.
    Examples:
        encode(0)     -> "0"
        encode(125)   -> "21"
        encode(12345) -> "3D7"
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    # Special case: zero
    if n == 0:
        return ALPHABET[0]
    chars = []
    while n > 0:
        n, remainder = divmod(n, BASE)
        chars.append(ALPHABET[remainder])
    # Digits are collected least-significant first
    return "".join(reversed(chars))


def decode(s: str) -> int:
    """Convert a base62 string back to its integer value.

    Examples:
        decode("0")   -> 0
        decode("21")  -> 125
        decode("3D7") -> 12345

    Raises ValueError if s contains characters outside the alphabet.
    """
    if not s:
        raise ValueError("input string cannot be empty")
    value_map = {char: i for i, char in enumerate(ALPHABET)}
    result = 0
    for char in s:
        if char not in value_map:
            raise ValueError(f"invalid base62 character: {char!r}")
        result = result * BASE + value_map[char]
    return result
