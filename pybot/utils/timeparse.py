from __future__ import annotations

import re
from datetime import timedelta


_DURATION_PATTERN = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$", re.IGNORECASE)
_MULTIPLIERS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}


def parse_duration(value: str) -> timedelta:
    """Parsea duraciones simples como 30m, 2h, 3d o 1w."""
    match = _DURATION_PATTERN.match(value)
    if not match:
        raise ValueError("Usá un formato como 30m, 2h, 3d o 1w.")

    amount = int(match.group(1))
    unit = match.group(2).lower()
    seconds = amount * _MULTIPLIERS[unit]

    if seconds <= 0:
        raise ValueError("La duración debe ser mayor que cero.")
    if seconds > 60 * 60 * 24 * 365:
        raise ValueError("El máximo permitido es 365 días.")

    return timedelta(seconds=seconds)
