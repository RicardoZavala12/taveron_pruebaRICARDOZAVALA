"""
Pruebas unitarias del modulo de cifrado y fingerprint.
"""

from app.core.crypto import (
    decrypt_identifier,
    encrypt_identifier,
    fingerprint_identifier,
    last_four,
    mask_identifier,
    normalize_identifier,
)


def test_encrypt_decrypt_roundtrip():
    original = "4111111111111111"
    cipher = encrypt_identifier(original)
    assert cipher != original
    assert decrypt_identifier(cipher) == original


def test_fingerprint_is_deterministic():
    a = fingerprint_identifier("4111 1111 1111 1111")
    b = fingerprint_identifier("4111111111111111")
    assert a == b


def test_fingerprint_changes_with_different_inputs():
    a = fingerprint_identifier("4111111111111111")
    b = fingerprint_identifier("4111111111111112")
    assert a != b


def test_normalize_strips_spaces_and_dashes():
    assert normalize_identifier("4111-1111 1111-1111") == "4111111111111111"


def test_last_four_returns_last_digits():
    assert last_four("4111-1111-1111-1234") == "1234"


def test_mask_hides_all_but_last_four():
    masked = mask_identifier("4111111111111111")
    assert masked.endswith("1111")
    assert "0000" not in masked
    assert "4111111111111111" not in masked
