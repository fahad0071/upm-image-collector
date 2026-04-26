"""Image storage — filename generation and file writing."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_RAW_IMAGES_DIR = Path("raw_images")


def generate_filepath(dt: datetime) -> Path:
    """Return the storage path for an image captured at *dt*.

    The filename encodes the UTC timestamp at millisecond granularity:
    ``raw_images/YYYYMMDD_HHMMSS_fff.jpg``

    Args:
        dt: A timezone-aware UTC datetime representing the capture instant.

    Returns:
        A :class:`~pathlib.Path` pointing to the target file (not yet created).

    Raises:
        ValueError: If *dt* is not timezone-aware.
    """
    if dt.tzinfo is None:
        raise ValueError("dt must be a timezone-aware datetime (UTC expected)")

    utc_dt = dt.astimezone(UTC)
    milliseconds = utc_dt.microsecond // 1000
    filename = utc_dt.strftime(f"%Y%m%d_%H%M%S_{milliseconds:03d}.jpg")
    return _RAW_IMAGES_DIR / filename


def save_image(data: bytes, dt: datetime) -> Path:
    """Write *data* to disk using the timestamp-based filename derived from *dt*.

    Creates ``raw_images/`` if it does not already exist.

    Args:
        data: Raw JPEG bytes to persist.
        dt: A timezone-aware UTC datetime used to build the filename.

    Returns:
        The :class:`~pathlib.Path` to which the image was written.

    Raises:
        ValueError: If *dt* is not timezone-aware.
        OSError: If the file cannot be written.
    """
    filepath = generate_filepath(dt)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(data)
    logger.debug("Wrote %d bytes to %s", len(data), filepath)
    return filepath
