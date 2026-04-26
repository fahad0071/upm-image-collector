"""Tests for image_collector.storage."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from image_collector.storage import generate_filepath, save_image

# ---------------------------------------------------------------------------
# generate_filepath
# ---------------------------------------------------------------------------


def test_generate_filepath_format() -> None:
    """Returned path matches raw_images/YYYYMMDD_HHMMSS_fff.jpg."""
    dt = datetime(2026, 4, 9, 22, 30, 1, 33_000, tzinfo=UTC)
    path = generate_filepath(dt)
    assert path == Path("raw_images/20260409_223001_033.jpg")


def test_generate_filepath_uses_milliseconds() -> None:
    """Millisecond component is zero-padded to three digits."""
    dt = datetime(2026, 1, 1, 0, 0, 0, 5_000, tzinfo=UTC)  # 5 ms
    path = generate_filepath(dt)
    assert path.name == "20260101_000000_005.jpg"


def test_generate_filepath_midnight_zero_ms() -> None:
    """Filepath is correct for exact midnight with zero milliseconds."""
    dt = datetime(2026, 4, 26, 0, 0, 0, 0, tzinfo=UTC)
    path = generate_filepath(dt)
    assert path.name == "20260426_000000_000.jpg"


def test_generate_filepath_raises_on_naive_datetime() -> None:
    """A naive datetime must raise ValueError."""
    dt = datetime(2026, 4, 9, 22, 30, 1)  # no tzinfo
    with pytest.raises(ValueError, match="timezone-aware"):
        generate_filepath(dt)


def test_generate_filepath_parent_is_raw_images() -> None:
    """The parent directory is always raw_images."""
    dt = datetime(2026, 6, 15, 12, 0, 0, 0, tzinfo=UTC)
    assert generate_filepath(dt).parent == Path("raw_images")


# ---------------------------------------------------------------------------
# save_image
# ---------------------------------------------------------------------------


def test_save_image_writes_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """save_image writes the supplied bytes to the generated filepath."""
    monkeypatch.chdir(tmp_path)
    dt = datetime(2026, 4, 9, 22, 30, 1, 33_000, tzinfo=UTC)
    data = b"\xff\xd8\xff" + b"\x00" * 10  # minimal JPEG-ish bytes

    saved_path = save_image(data, dt)

    assert saved_path.exists()
    assert saved_path.read_bytes() == data


def test_save_image_creates_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """raw_images/ is created automatically if it does not exist."""
    monkeypatch.chdir(tmp_path)
    dt = datetime(2026, 4, 9, 22, 30, 1, 0, tzinfo=UTC)

    assert not (tmp_path / "raw_images").exists()
    save_image(b"data", dt)
    assert (tmp_path / "raw_images").is_dir()


def test_save_image_returns_correct_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Returned path equals generate_filepath(dt)."""
    monkeypatch.chdir(tmp_path)
    dt = datetime(2026, 4, 9, 22, 30, 1, 33_000, tzinfo=UTC)
    returned = save_image(b"img", dt)
    assert returned == generate_filepath(dt)


def test_save_image_raises_on_naive_datetime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """save_image must raise ValueError for naive datetimes."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="timezone-aware"):
        save_image(b"data", datetime(2026, 1, 1))
