"""Test pytchdeck."""

import pytchdeck


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(pytchdeck.__name__, str)
