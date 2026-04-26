"""Scheduler — random timestamp generation and precision sleep logic."""

from __future__ import annotations

import logging
import random
import time
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

_WINDOW_MINUTES = 10


def generate_schedule(target_time: datetime, n: int = 100) -> list[datetime]:
    """Generate *n* random UTC datetimes in ``[target_time - 10 min, target_time)``.

    The returned list is sorted in ascending order so the caller can process
    timestamps sequentially without additional sorting.

    Args:
        target_time: The exclusive upper bound.  Must be timezone-aware.
        n: Number of timestamps to generate.  Defaults to 100.

    Returns:
        A sorted list of *n* timezone-aware UTC datetimes.

    Raises:
        ValueError: If *target_time* is not timezone-aware or *n* is not positive.
    """
    if target_time.tzinfo is None:
        raise ValueError("target_time must be a timezone-aware datetime (UTC expected)")
    if n <= 0:
        raise ValueError(f"n must be a positive integer, got {n}")

    window_start = target_time - timedelta(minutes=_WINDOW_MINUTES)
    window_seconds = _WINDOW_MINUTES * 60  # 600 seconds

    timestamps: list[datetime] = []
    for _ in range(n):
        offset_seconds = random.uniform(0, window_seconds)
        ts = window_start + timedelta(seconds=offset_seconds)
        # Clamp microseconds so we do not accidentally reach target_time
        if ts >= target_time:
            ts = target_time - timedelta(microseconds=1)
        timestamps.append(ts.astimezone(UTC))

    timestamps.sort()
    logger.debug(
        "Generated %d timestamps between %s and %s",
        n,
        window_start.isoformat(),
        target_time.isoformat(),
    )
    return timestamps


def wait_until(dt: datetime) -> None:
    """Block until *dt* (UTC).

    If *dt* is already in the past the function returns immediately without
    sleeping, logging a warning so the caller knows the slot was missed.

    Args:
        dt: A timezone-aware datetime representing the earliest moment to resume.

    Raises:
        ValueError: If *dt* is not timezone-aware.
    """
    if dt.tzinfo is None:
        raise ValueError("dt must be a timezone-aware datetime (UTC expected)")

    now = datetime.now(UTC)
    delay = (dt - now).total_seconds()

    if delay <= 0:
        logger.warning(
            "Target time %s is already in the past (%.3f s ago); skipping sleep",
            dt.isoformat(),
            -delay,
        )
        return

    logger.debug("Sleeping %.3f s until %s", delay, dt.isoformat())
    time.sleep(delay)
