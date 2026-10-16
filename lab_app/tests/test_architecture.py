"""Structural rules from the requirements, checked by reading the source (no execution)."""
import ast
import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
SOURCES = sorted(p for p in APP_DIR.rglob("*.py") if "tests" not in p.parts)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imports(tree: ast.Module) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("path", [p for p in SOURCES if p.name != "harness.py"], ids=lambda p: p.name)
def test_app_process_never_execs_user_code(path):
    """Requirement 6: user code must not run inside the app via exec/eval."""
    calls = [n.func.id for n in ast.walk(_tree(path))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("exec", "eval")]
    assert calls == [], f"{path.name} calls {calls}"


def test_harness_uses_only_the_standard_library():
    """The child runs with -I, so it cannot import the app package or third-party modules."""
    top_level = {name.split(".")[0] for name in _imports(_tree(APP_DIR / "core" / "harness.py"))}
    assert top_level <= set(sys.stdlib_module_names), top_level - set(sys.stdlib_module_names)


def test_harness_is_not_imported_by_the_app():
    importers = [p.name for p in SOURCES if any("harness" in m for m in _imports(_tree(p)))]
    assert importers == []


@pytest.mark.parametrize("path", sorted((APP_DIR / "views").glob("*.py")) + [APP_DIR / "components.py", APP_DIR / "app.py"],
                         ids=lambda p: p.name)
def test_ui_does_not_touch_storage_directly(path):
    """UI code goes through LearningService; SQL lives only in core/repository.py."""
    forbidden = {"sqlite3", "lab_app.core.repository", "lab_app.core.db", "lab_app.core.runner"}
    assert _imports(_tree(path)) & forbidden == set()


def test_sql_lives_in_repository_and_db_only():
    users = sorted(p.name for p in SOURCES if "sqlite3" in _imports(_tree(p)))
    assert users == ["db.py", "repository.py"]
