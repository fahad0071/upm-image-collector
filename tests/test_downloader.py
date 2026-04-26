"""Tests for image_collector.downloader."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from image_collector.downloader import DownloadError, download_image

_URL = "https://thispersondoesnotexist.com/"
_FAKE_IMAGE = b"\xff\xd8\xff" + b"\x00" * 100

_PATCH_GET = "image_collector.downloader.requests.get"
_PATCH_SLEEP = "image_collector.downloader.time.sleep"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(content: bytes = _FAKE_IMAGE, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.content = content
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    return resp


def _make_http_error(status_code: int = 500) -> requests.HTTPError:
    resp = MagicMock()
    resp.status_code = status_code
    return requests.HTTPError(response=resp)


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------


def test_download_image_returns_bytes_on_success() -> None:
    """A successful request returns the raw response bytes."""
    mock_resp = _make_response()
    with patch(_PATCH_GET, return_value=mock_resp):
        result = download_image(_URL)
    assert result == _FAKE_IMAGE


def test_download_image_sends_user_agent() -> None:
    """The request includes a User-Agent header."""
    mock_resp = _make_response()
    with patch(_PATCH_GET, return_value=mock_resp) as mock_get:
        download_image(_URL)
    _, kwargs = mock_get.call_args
    assert "User-Agent" in kwargs["headers"]
    assert kwargs["headers"]["User-Agent"]  # non-empty


def test_download_image_uses_timeout() -> None:
    """The request sets a timeout."""
    mock_resp = _make_response()
    with patch(_PATCH_GET, return_value=mock_resp) as mock_get:
        download_image(_URL)
    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") is not None


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------


def test_download_image_retries_on_connection_error() -> None:
    """Transient connection errors trigger retries."""
    mock_resp = _make_response()
    side_effects = [requests.ConnectionError("refused"), mock_resp]
    with patch(_PATCH_GET, side_effect=side_effects), patch(_PATCH_SLEEP):
        result = download_image(_URL, retries=2)
    assert result == _FAKE_IMAGE


def test_download_image_retries_on_http_error() -> None:
    """HTTP 5xx errors trigger retries."""
    good_resp = _make_response()
    bad_resp = _make_response(status_code=503)
    bad_resp.raise_for_status.side_effect = _make_http_error(503)

    side_effects = [bad_resp, good_resp]
    with patch(_PATCH_GET, side_effect=side_effects), patch(_PATCH_SLEEP):
        result = download_image(_URL, retries=2)
    assert result == _FAKE_IMAGE


def test_download_image_raises_after_all_retries_exhausted() -> None:
    """DownloadError is raised once every attempt fails."""
    with (
        patch(_PATCH_GET, side_effect=requests.ConnectionError("refused")),
        patch(_PATCH_SLEEP),
        pytest.raises(DownloadError),
    ):
        download_image(_URL, retries=3)


def test_download_image_correct_retry_count() -> None:
    """requests.get is called exactly `retries` times when every attempt fails."""
    with (
        patch(
            _PATCH_GET,
            side_effect=requests.ConnectionError("refused"),
        ) as mock_get,
        patch(_PATCH_SLEEP),
        pytest.raises(DownloadError),
    ):
        download_image(_URL, retries=4)
    assert mock_get.call_count == 4


def test_download_image_raises_on_invalid_retries() -> None:
    """retries < 1 must raise ValueError."""
    with pytest.raises(ValueError, match="retries must be at least 1"):
        download_image(_URL, retries=0)


# ---------------------------------------------------------------------------
# DownloadError
# ---------------------------------------------------------------------------


def test_download_error_is_exception() -> None:
    """DownloadError is a subclass of Exception."""
    assert issubclass(DownloadError, Exception)
