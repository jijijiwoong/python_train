"""AST-based static checks: the readability/logic side of grading (content_schema.md §3.3).

Parses the code only — never executes it — so it is safe to run in the app process.
"""
from __future__ import annotations

import ast
from typing import Any

from lab_app.core.models import Feedback

SUPPORTED_SYNTAX: dict[str, tuple[tuple[type[ast.AST], ...], str]] = {
    "for": ((ast.For, ast.AsyncFor), "for 반복문"),
    "while": ((ast.While,), "while 반복문"),
    "if": ((ast.If, ast.IfExp), "if 조건문"),
    "def": ((ast.FunctionDef, ast.AsyncFunctionDef), "함수 정의(def)"),
    "return": ((ast.Return,), "return 문"),
    "fstring": ((ast.JoinedStr,), "f-string"),
    "import": ((ast.Import, ast.ImportFrom), "import 문"),
    "list_comp": ((ast.ListComp,), "리스트 컴프리헨션"),
    "try": ((ast.Try, ast.TryStar), "try/except"),
}

LONG_LINE = 100


def _uses(tree: ast.AST, name: str) -> ast.AST | None:
    node_types = SUPPORTED_SYNTAX[name][0]
    return next((n for n in ast.walk(tree) if isinstance(n, node_types)), None)


def _called_names(tree: ast.AST) -> list[tuple[str, int]]:
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.append((func.id, node.lineno))
            elif isinstance(func, ast.Attribute):
                calls.append((func.attr, node.lineno))
    return calls


def code_lines(code: str) -> int:
    """Lines that are neither blank nor comments."""
    return sum(1 for line in code.splitlines() if line.strip() and not line.strip().startswith("#"))


def run_static_checks(code: str, checks: dict[str, Any] | None) -> list[Feedback]:
    """Return feedback for exercise-specific rules plus general readability warnings.

    Code with a syntax error yields no feedback: the runner reports the syntax error itself.
    """
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return []
    checks = checks or {}
    feedback: list[Feedback] = []

    for name in checks.get("required_syntax", []):
        if _uses(tree, name) is None:
            feedback.append(Feedback("logic", "error", f"이 문제에서는 {SUPPORTED_SYNTAX[name][1]}을(를) 사용해야 합니다."))
    for name in checks.get("forbidden_syntax", []):
        node = _uses(tree, name)
        if node is not None:
            feedback.append(Feedback("logic", "error", f"이 문제에서는 {SUPPORTED_SYNTAX[name][1]}을(를) 사용할 수 없습니다.",
                                     line=getattr(node, "lineno", None)))
    forbidden_calls = set(checks.get("forbidden_calls", []))
    for name, lineno in _called_names(tree):
        if name in forbidden_calls:
            feedback.append(Feedback("logic", "error", f"이 문제에서는 {name}()을(를) 사용할 수 없습니다. 직접 구현해 보세요.",
                                     line=lineno))
            forbidden_calls.discard(name)  # report each name once

    max_lines = checks.get("max_lines")
    n = code_lines(code)
    if max_lines and n > max_lines:
        feedback.append(Feedback("readability", "warning",
                                 f"코드가 {n}줄입니다. {max_lines}줄 이내로 더 간결하게 작성할 수 있어요."))
    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > LONG_LINE:
            feedback.append(Feedback("readability", "warning", f"{i}번째 줄이 {LONG_LINE}자를 넘습니다. 줄을 나누면 읽기 쉬워요.", line=i))
            break
    if any("\t" in line[: len(line) - len(line.lstrip())] for line in code.splitlines()):
        feedback.append(Feedback("readability", "warning", "들여쓰기에 탭 문자가 있습니다. 공백 4칸을 권장합니다."))
    return feedback
