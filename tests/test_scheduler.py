"""Tests for image_collector.scheduler."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from image_collector.scheduler import generate_schedule, wait_until

_TARGET = datetime(2026, 4, 26, 23, 0, 0, tzinfo=UTC)
_WINDOW_START = _TARGET - timedelta(minutes=10)


# ---------------------------------------------------------------------------
# generate_schedule
# ---------------------------------------------------------------------------


def test_generate_schedule_returns_correct_count() -> None:
    """Returned list contains exactly n timestamps."""
    schedule = generate_schedule(_TARGET, n=100)
    assert len(schedule) == 100


def test_generate_schedule_custom_count() -> None:
    """Returned list length matches the requested count."""
    schedule = generate_schedule(_TARGET, n=7)
    assert len(schedule) == 7


def test_generate_schedule_all_within_window() -> None:
    """Every timestamp is in [target - 10 min, target)."""
    schedule = generate_schedule(_TARGET, n=200)
    for ts in schedule:
        assert _WINDOW_START <= ts < _TARGET, f"Timestamp {ts} is outside the window"


def test_generate_schedule_sorted_ascending() -> None:
    """Returned schedule is sorted in ascending order."""
    schedule = generate_schedule(_TARGET, n=50)
    assert schedule == sorted(schedule)


def test_generate_schedule_all_utc_aware() -> None:
    """Every timestamp is timezone-aware (UTC)."""
    schedule = generate_schedule(_TARGET, n=20)
    for ts in schedule:
        assert ts.tzinfo is not None
        assert ts.tzinfo.utcoffset(ts) == timedelta(0)


def test_generate_schedule_raises_on_naive_target() -> None:
    """A naive target_time must raise ValueError."""
    naive = datetime(2026, 4, 26, 23, 0, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        generate_schedule(naive)


def test_generate_schedule_raises_on_zero_count() -> None:
    """n=0 must raise ValueError."""
    with pytest.raises(ValueError, match="positive integer"):
        generate_schedule(_TARGET, n=0)


def test_generate_schedule_raises_on_negative_count() -> None:
    """Negative n must raise ValueError."""
    with pytest.raises(ValueError, match="positive integer"):
        generate_schedule(_TARGET, n=-5)


# ---------------------------------------------------------------------------
# wait_until
# ---------------------------------------------------------------------------


def test_wait_until_sleeps_correct_duration() -> None:
    """wait_until calls time.sleep with the correct delay."""
    future = datetime(2099, 1, 1, tzinfo=UTC)
    fake_now = future - timedelta(seconds=5)
    with (
        patch("image_collector.scheduler.time.sleep") as mock_sleep,
        patch("image_collector.scheduler.datetime") as mock_dt,
    ):
        mock_dt.now.return_value = fake_now
        wait_until(future)

    mock_sleep.assert_called_once()
    delay = mock_sleep.call_args[0][0]
    assert 4.9 <= delay <= 5.1


def test_wait_until_skips_past_timestamps(caplog: pytest.LogCaptureFixture) -> None:
    """wait_until does not sleep when the target is already in the past."""
    past = datetime(2000, 1, 1, tzinfo=UTC)
    with patch("image_collector.scheduler.time.sleep") as mock_sleep:
        import logging

        with caplog.at_level(logging.WARNING, logger="image_collector.scheduler"):
            wait_until(past)
        mock_sleep.assert_not_called()
    assert "past" in caplog.text.lower()


def test_wait_until_raises_on_naive_datetime() -> None:
    """wait_until must raise ValueError for a naive datetime."""
    with pytest.raises(ValueError, match="timezone-aware"):
        wait_until(datetime(2099, 1, 1))
