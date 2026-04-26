# UPM Image Collector

A production-quality Python pipeline that downloads face images from
[thispersondoesnotexist.com](https://thispersondoesnotexist.com/) and saves
them to local storage as a timestamped dataset.  The pipeline accepts a future
**target time** and distributes all downloads randomly across the **10-minute
window immediately before** that time, recording each image under a
millisecond-precision UTC filename (`raw_images/YYYYMMDD_HHMMSS_fff.jpg`).
This makes the dataset self-documenting and collision-free without any
additional registry.

---

## Installation

Python 3.11 or later is required.

```bash
# 1. Clone the repository
git clone <repo-url>
cd upm-image-collector

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the project and all development dependencies
pip install -e ".[dev]"
```

---

## Usage

### Collect 100 images

```bash
image-collector --target 2026-04-26T23:00:00Z
```

The command blocks until the 10-minute window opens, then downloads one image
per scheduled timestamp and prints progress as each file is saved:

```
2026-04-26T22:51:03  INFO     image_collector.pipeline — [001/100] Saved raw_images/20260426_225103_412.jpg
2026-04-26T22:51:47  INFO     image_collector.pipeline — [002/100] Saved raw_images/20260426_225147_088.jpg
...
```

### Dry run — preview the schedule without downloading

```bash
image-collector --target 2026-04-26T23:00:00Z --dry-run
```

### Custom count and log verbosity

```bash
image-collector --target 2026-04-26T23:00:00Z --count 50 --log-level DEBUG
```

### All options

```
usage: image-collector [-h] --target DATETIME [--count N] [--dry-run]
                       [--log-level {DEBUG,INFO,WARNING}]

options:
  --target DATETIME     Future UTC target time in ISO 8601 format,
                        e.g. 2026-04-26T23:00:00Z
  --count N             Number of images to download (default: 100)
  --dry-run             Print the planned schedule without downloading
  --log-level           Logging verbosity: DEBUG / INFO / WARNING (default: INFO)
```

---

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=image_collector --cov-report=term-missing
```

---

## Code Quality Checks

```bash
ruff check .                # linting
ruff format --check .       # formatting
mypy src/                   # static type checking
```

Run all checks at once:

```bash
ruff check . && ruff format --check . && mypy src/ && pytest
```

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full sequence diagram
and component descriptions.

---

## Project Structure

```
upm-image-collector/
├── src/
│   └── image_collector/
│       ├── __init__.py       # package version and exports
│       ├── downloader.py     # HTTP fetch with retry + exponential back-off
│       ├── scheduler.py      # random timestamp generation and precision sleep
│       ├── storage.py        # millisecond filename generation and file writing
│       └── pipeline.py       # CLI entry point, orchestrates the pipeline
├── tests/
│   ├── test_downloader.py
│   ├── test_scheduler.py
│   └── test_storage.py
├── docs/
│   └── architecture.md       # system diagram (Mermaid)
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions: lint + type-check + test
├── pyproject.toml
├── README.md
├── .gitignore
└── CLAUDE.md
```
