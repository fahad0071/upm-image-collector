# UPM Image Collector

Image Collector is a Python pipeline that downloads face images from [thispersondoesnotexist.com](https://thispersondoesnotexist.com/) and stores them locally as a timestamped dataset.

The system accepts a **future target time** and distributes all downloads randomly across the **10-minute window immediately before that time**.

Each image is saved using a UTC timestamp with millisecond precision:

```text
raw_images/YYYYMMDD_HHMMSS_fff.jpg
```

Example:

```text
raw_images/20260426_225103_412.jpg
```

This keeps every file unique, ordered, and easy to trace.

---

# Features

- Downloads images from a live source
- Collects images over time instead of all at once
- Randomized scheduling within the required 10-minute window
- Millisecond-precision UTC filenames
- Retry logic with timeout handling
- CLI interface
- Dry-run mode for schedule preview
- Logging and progress tracking
- Unit tests and CI-ready structure

---

# Installation

Python 3.11+ recommended.

## Clone Repository

```bash
git clone https://github.com/fahad0071/upm-image-collector
cd upm-image-collector
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -e ".[dev]"
```

---

# Usage

## Collect 100 Images

```bash
image-collector --target 2026-04-26T23:00:00Z
```

Example output:

```text
2026-04-26T22:51:03 INFO [001/100] Saved raw_images/20260426_225103_412.jpg
2026-04-26T22:51:47 INFO [002/100] Saved raw_images/20260426_225147_088.jpg
...
```

## Preview Schedule Only

```bash
image-collector --target 2026-04-26T23:00:00Z --dry-run
```

## Download Custom Number of Images

```bash
image-collector --target 2026-04-26T23:00:00Z --count 50
```

## Debug Logging

```bash
image-collector --target 2026-04-26T23:00:00Z --log-level DEBUG
```

---

# Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=image_collector --cov-report=term-missing
```

---

# Code Quality

```bash
ruff check .
ruff format --check .
mypy src/
```

Run all checks:

```bash
ruff check . && ruff format --check . && mypy src/ && pytest
```

---

## Architecture

The system diagram (sequence + data flow) is in [docs/architecture.md](docs/architecture.md).

---

# Project Structure

```text
upm-image-collector/
├── src/
│   └── image_collector/
│       ├── __init__.py
│       ├── downloader.py        
│       ├── scheduler.py         
│       ├── storage.py           
│       └── pipeline.py          
│
├── tests/
│   ├── test_downloader.py
│   ├── test_scheduler.py
│   └── test_storage.py
│
├── docs/
│   └── architecture.md         
│       └── architecture_diagram.png
│ 
├── .github/
│   └── workflows/
│       └── ci.yml             
│
├── pyproject.toml
├── README.md
└── .gitignore
```

---

# Reliability Considerations

- Retry handling for temporary network failures
- Timeout protection
- Unique filenames
- Structured logs
- Modular architecture

---

# Future Improvements

- Parallel downloads
- Metadata export
- Resume interrupted runs
- Docker packaging
- Cloud storage support

---

# License

For assessment / educational use.
