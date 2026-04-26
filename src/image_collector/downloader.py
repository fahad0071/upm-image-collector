"""Image downloader — HTTP fetch with retry and exponential back-off."""

from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_TIMEOUT_SECONDS = 15


class DownloadError(Exception):
    """Raised when an image cannot be fetched after all retry attempts."""


def download_image(
    url: str,
    retries: int = 3,
    backoff: float = 1.0,
) -> bytes:
    """Fetch raw image bytes from *url*, retrying on transient failures.

    On each failure the function waits ``backoff * 2^attempt`` seconds before
    the next attempt (exponential back-off).  If every attempt fails a
    :class:`DownloadError` is raised.

    Args:
        url: The URL to fetch.
        retries: Maximum number of attempts.  Must be at least 1.
        backoff: Base back-off duration in seconds.  Multiplied by ``2^attempt``
            on each successive failure.

    Returns:
        The raw response body as :class:`bytes`.

    Raises:
        DownloadError: After all *retries* are exhausted without a successful
            response.
        ValueError: If *retries* is less than 1.
    """
    if retries < 1:
        raise ValueError(f"retries must be at least 1, got {retries}")

    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            logger.debug("GET %s (attempt %d/%d)", url, attempt + 1, retries)
            response = requests.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            logger.debug("Received %d bytes from %s", len(response.content), url)
            return response.content
        except requests.RequestException as exc:
            last_error = exc
            wait = backoff * (2**attempt)
            logger.warning(
                "Download attempt %d/%d failed: %s — retrying in %.1f s",
                attempt + 1,
                retries,
                exc,
                wait,
            )
            if attempt < retries - 1:
                time.sleep(wait)

    raise DownloadError(
        f"Failed to download {url} after {retries} attempt(s)"
    ) from last_error
