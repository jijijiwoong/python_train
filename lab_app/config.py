"""Paths and limits. Environment variables override paths (tests use temporary ones)."""
import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

CONTENT_DIR = Path(os.environ.get("LAB_CONTENT_DIR", APP_DIR / "content"))
DB_PATH = Path(os.environ.get("LAB_DB_PATH", APP_DIR / "data" / "learning.db"))

# Code execution limits (see 01_design/architecture.md §4.3)
RUN_TIMEOUT_SEC = 5.0
MAX_STDOUT_CHARS = 20_000
MAX_STDERR_CHARS = 10_000
MAX_READ_BYTES = 256 * 1024          # raw stdout/stderr files of the child process
MAX_RESULT_BYTES = 8 * 1024 * 1024   # result.jsonl written by the harness
MAX_FIGURE_BYTES = 2 * 1024 * 1024   # each matplotlib PNG shown after a free run

# Learning rules
BLANK_TOKEN = "____"
SOLUTION_UNLOCK_ATTEMPTS = 1
WEAK_MIN_SUBMISSIONS = 2
WEAK_FAIL_RATE = 0.5

LLM_PROVIDER = os.environ.get("LAB_LLM_PROVIDER", "none")
