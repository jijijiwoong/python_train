"""Helpers for data-library lessons: expected output of concept examples is produced by running them here."""
import io
import os
import sys
from pathlib import Path
from contextlib import redirect_stdout
from textwrap import dedent

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MATPLOTLIBRC", str(Path(__file__).resolve().parents[2] / "lab_app" / "core" / "matplotlibrc"))

from cb_common import code  # noqa: E402


def run_block(src):
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(dedent(src).lstrip("\n"), "<block>", "exec"), {"__name__": "__main__"})
    try:
        import matplotlib.pyplot as plt
        plt.close("all")
    except ImportError:
        pass
    return buf.getvalue()


def ncode(src, time_limit=None):
    b = code(src, run_block(src))
    if time_limit:
        b["time_limit_sec"] = time_limit
    return b
