# CLAUDE.md — UPM Image Collector

This file is the source of truth for Claude Code working on this project.
Read it fully before writing any code, making commits, or suggesting changes.

---

## Project Overview

This is a **production-quality Python pipeline** that downloads 100 face images
from `https://thispersondoesnotexist.com/` and saves them to local storage using
millisecond-precision UTC timestamps as filenames.

The pipeline accepts a **future target time** and distributes the 100 downloads
randomly across the **10-minute window immediately before** that target time
(not including the target time itself).

This is a **Summer Trainee coding task** for UPM (a real company). It will be
reviewed by engineers. Quality, maintainability, and professionalism matter far
more than clever code.

---

## Submission Requirements

- Private GitHub repo
- Deadline: **23:59 EEST Sunday April 26, 2026**
- Collaborators to add at the very end (after all code is done):
  - `catherine.fait@upm.com`
  - `jani.strandberg@upm.com`
- Send email with repo link once submitted

---

## Functional Requirements

### Requirement 1 — Save 100 images
- Source: `https://thispersondoesnotexist.com/`
- Save path: `raw_images/<yyyymmdd_hhmmss_fff>.jpg`
- Timestamp format: UTC, millisecond granularity
- Example: `raw_images/20260409_223001_033.jpg`

### Requirement 2 — Scheduled random sampling
- Accept a future `target_time` (UTC) as CLI input
- Generate 100 random timestamps in the half-open interval `[target_time - 10min, target_time)`
- Sort timestamps ascending
- Sleep until each timestamp, then download and save the image
- If script is launched before the window opens, it should wait

---

## Project Structure

```
upm-image-collector/
├── src/
│   └── image_collector/
│       ├── __init__.py          # version + package exports
│       ├── downloader.py        # HTTP fetch with retry logic
│       ├── scheduler.py         # random timestamp generation + sleep logic
│       ├── storage.py           # filename generation + file writing
│       └── pipeline.py          # CLI entrypoint, orchestrates everything
├── tests/
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_scheduler.py
│   └── test_storage.py
├── docs/
│   └── architecture.md          # required system diagram (Mermaid)
├── .github/
│   └── workflows/
│       └── ci.yml               # lint + test on every push
├── raw_images/                  # gitignored, created at runtime
├── pyproject.toml
├── README.md
├── .gitignore
└── CLAUDE.md                    # this file
```

---

## Module Responsibilities

### `storage.py`
- `generate_filepath(dt: datetime) -> Path`
  - Takes a UTC datetime, returns `raw_images/YYYYMMDD_HHMMSS_fff.jpg`
- `save_image(data: bytes, dt: datetime) -> Path`
  - Creates `raw_images/` if it doesn't exist
  - Writes bytes to the generated filepath
  - Returns the path it saved to

### `scheduler.py`
- `generate_schedule(target_time: datetime, n: int = 100) -> list[datetime]`
  - Generates `n` random UTC datetimes in `[target_time - 10min, target_time)`
  - Returns them sorted ascending
- `wait_until(dt: datetime) -> None`
  - Sleeps until the given UTC datetime
  - Should handle the case where `dt` is already in the past (skip gracefully)

### `downloader.py`
- `download_image(url: str, retries: int = 3, backoff: float = 1.0) -> bytes`
  - Fetches image bytes from the given URL
  - Retries on failure with exponential backoff
  - Raises `DownloadError` (custom exception) after all retries exhausted
  - Sets a realistic User-Agent header

### `pipeline.py`
- CLI entrypoint using `argparse`
- Arguments:
  - `--target` — ISO 8601 UTC datetime string e.g. `2026-04-26T23:00:00Z`
  - `--count` — number of images, default 100
  - `--dry-run` — print schedule without downloading
  - `--log-level` — DEBUG / INFO / WARNING, default INFO
- Wires scheduler → downloader → storage
- Uses `logging` (not `print`) throughout
- Shows progress: `[42/100] Saved raw_images/20260426_225301_044.jpg`

---

## Code Quality Rules

- **Type hints on every function** — parameters and return types
- **Docstrings on every public function** — one-line summary minimum
- **No bare `except`** — always catch specific exceptions
- **No `print()`** — use `logging` module only
- **All datetimes must be timezone-aware UTC** — use `datetime.now(UTC)`
- **Never hardcode the URL** — pass it as a parameter or constant in `pipeline.py`
- **Line length**: 88 characters (ruff default)
- **Imports**: sorted and grouped (ruff handles this)

---

## Tooling

| Tool | Purpose | Command |
|------|---------|---------|
| `ruff` | Linting + formatting | `ruff check . && ruff format .` |
| `mypy` | Static type checking | `mypy src/` |
| `pytest` | Unit tests | `pytest` |
| `pytest-cov` | Coverage report | `pytest --cov=image_collector` |

Run all checks before every commit:
```bash
ruff check . && ruff format . && mypy src/ && pytest
```

---

## Commit Strategy

Make **one commit per logical unit**. Never commit broken or untested code.
Commit messages follow this format: `type: short description`

Types: `chore`, `feat`, `fix`, `test`, `docs`, `ci`, `refactor`

---

## Testing Guidelines

- Tests live in `tests/`, mirroring `src/image_collector/`
- **Do not make real HTTP requests in tests** — mock `requests.get`
- Test file I/O using `tmp_path` fixture (pytest built-in)
- Each test function tests **one behavior**
- Name tests descriptively: `test_generate_filepath_uses_utc_milliseconds`

---

## What NOT to Do

- Do not use `asyncio` — keep it simple and synchronous
- Do not use `time.sleep()` with a fixed interval loop — calculate exact sleep durations
- Do not store images in git — `raw_images/` is gitignored
- Do not use `print()` anywhere in `src/`
- Do not leave TODO comments in committed code
- Do not make real HTTP calls in tests
- Do not add collaborators to GitHub until all code is pushed and ready

---

## How to Run (Once Built)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run with a target time (images download in the 10 min before this)
image-collector --target 2026-04-26T23:00:00Z

# Dry run — shows schedule without downloading
image-collector --target 2026-04-26T23:00:00Z --dry-run

# Custom count and log level
image-collector --target 2026-04-26T23:00:00Z --count 100 --log-level DEBUG
```

---

## Final Checklist Before Adding Collaborators

- [ ] All code passes `ruff check .`
- [ ] All code passes `ruff format --check .`
- [ ] All code passes `mypy src/`
- [ ] All tests pass with `pytest`
- [ ] CI is green on GitHub Actions
- [ ] `raw_images/` is gitignored and not in the repo
- [ ] `docs/architecture.md` has the Mermaid diagram
- [ ] README is complete with setup + usage instructions
- [ ] Commit history is clean and meaningful
- [ ] No debug code, no TODOs, no commented-out blocks
- [ ] Add collaborators: `catherine.fait@upm.com`, `jani.strandberg@upm.com`
- [ ] Send email with repo link
