"""CLI pipeline — orchestrates scheduler, downloader, and storage."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime

from image_collector.downloader import DownloadError, download_image
from image_collector.scheduler import generate_schedule, wait_until
from image_collector.storage import save_image

_SOURCE_URL = "https://thispersondoesnotexist.com/"

_LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _configure_logging(level: str) -> None:
    """Set up root logger with a human-readable format."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(format=_LOG_FORMAT, datefmt=_DATE_FORMAT, level=numeric)


def _parse_target(raw: str) -> datetime:
    """Parse an ISO 8601 UTC string into a timezone-aware :class:`datetime`.

    Accepts the trailing ``Z`` suffix as well as ``+00:00``.

    Args:
        raw: ISO 8601 string, e.g. ``2026-04-26T23:00:00Z``.

    Returns:
        A timezone-aware UTC :class:`datetime`.

    Raises:
        argparse.ArgumentTypeError: If the string cannot be parsed.
    """
    normalised = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalised)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Cannot parse '{raw}' as ISO 8601 datetime: {exc}"
        ) from exc

    if dt.tzinfo is None:
        raise argparse.ArgumentTypeError(
            f"'{raw}' has no timezone; append 'Z' or '+00:00' for UTC."
        )
    return dt.astimezone(UTC)


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="image-collector",
        description=(
            "Download face images from thispersondoesnotexist.com and save "
            "them to raw_images/ using millisecond-precision UTC filenames. "
            "All downloads occur within the 10-minute window before TARGET."
        ),
    )
    parser.add_argument(
        "--target",
        required=True,
        metavar="DATETIME",
        type=_parse_target,
        help=(
            "Future UTC target time in ISO 8601 format, "
            "e.g. 2026-04-26T23:00:00Z.  "
            "Images are saved in [target-10min, target)."
        ),
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        metavar="N",
        help="Number of images to download (default: 100).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned schedule without downloading anything.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING"],
        help="Logging verbosity (default: INFO).",
    )
    return parser


def run(
    target_time: datetime,
    count: int = 100,
    url: str = _SOURCE_URL,
    dry_run: bool = False,
) -> int:
    """Execute the download pipeline.

    Generates a schedule of *count* random timestamps in the 10-minute window
    before *target_time*, waits for each one, then downloads and saves the
    image.

    Args:
        target_time: Exclusive upper bound of the download window (UTC).
        count: Number of images to download.
        url: Image source URL.
        dry_run: If ``True``, print the schedule and return without downloading.

    Returns:
        The number of images successfully saved.
    """
    logger = logging.getLogger(__name__)

    logger.info(
        "Generating schedule: %d images before %s", count, target_time.isoformat()
    )
    schedule = generate_schedule(target_time, n=count)

    if dry_run:
        logger.info("Dry run — printing schedule only, no downloads will occur.")
        for idx, ts in enumerate(schedule, start=1):
            print(f"[{idx:>{len(str(count))}}/{count}] {ts.isoformat()}")  # noqa: T201
        return 0

    saved = 0
    width = len(str(count))

    for idx, ts in enumerate(schedule, start=1):
        wait_until(ts)

        try:
            image_bytes = download_image(url)
        except DownloadError:
            logger.error(
                "[%0*d/%d] Download failed; skipping timestamp %s",
                width,
                idx,
                count,
                ts.isoformat(),
            )
            continue

        filepath = save_image(image_bytes, ts)
        saved += 1
        logger.info("[%0*d/%d] Saved %s", width, idx, count, filepath)

    logger.info("Pipeline complete: %d/%d images saved.", saved, count)
    return saved


def main() -> None:
    """Entry point registered as the ``image-collector`` console script."""
    parser = _build_parser()
    args = parser.parse_args()

    _configure_logging(args.log_level)
    logger = logging.getLogger(__name__)

    now = datetime.now(UTC)
    if args.target <= now:
        logger.error(
            "Target time %s is in the past (now: %s). "
            "Please provide a future UTC datetime.",
            args.target.isoformat(),
            now.isoformat(),
        )
        sys.exit(1)

    run(
        target_time=args.target,
        count=args.count,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
