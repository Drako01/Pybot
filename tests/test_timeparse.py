from datetime import timedelta

import pytest

from pybot.utils.timeparse import parse_duration


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("30s", timedelta(seconds=30)),
        ("15m", timedelta(minutes=15)),
        ("2h", timedelta(hours=2)),
        ("3d", timedelta(days=3)),
        ("1w", timedelta(weeks=1)),
        (" 10M ", timedelta(minutes=10)),
    ],
)
def test_parse_duration_valid(raw: str, expected: timedelta) -> None:
    assert parse_duration(raw) == expected


@pytest.mark.parametrize("raw", ["", "mañana", "10", "-2h", "1y", "999w"])
def test_parse_duration_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_duration(raw)
