"""Test pytchdeck."""

import pytchdeck


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(pytchdeck.__name__, str)
