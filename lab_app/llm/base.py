"""LLM extension points (not used in the MVP). See 01_design/architecture.md §8.

A future provider implements these protocols; the grader and UI only depend on them.
Any LLM hint must follow the same rule as static hints: never write out the full solution.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from lab_app.core.models import Exercise, Feedback, GradeResult


class CodeReviewer(Protocol):
    def review(self, exercise: Exercise, code: str, result: GradeResult) -> list[Feedback]: ...


class HintProvider(Protocol):
    def hint(self, exercise: Exercise, code: str, result: GradeResult | None, level: int) -> str | None: ...


class NullReviewer:
    """Default reviewer: adds nothing."""

    def review(self, exercise: Exercise, code: str, result: GradeResult) -> list[Feedback]:
        return []


class StaticHintProvider:
    """Default hints: the exercise's own staged hints from JSON (level is 1-based)."""

    def hint(self, exercise: Exercise, code: str, result: GradeResult | None, level: int) -> str | None:
        return exercise.hints[level - 1] if 1 <= level <= len(exercise.hints) else None


def get_reviewer(provider: str = "none") -> CodeReviewer | None:
    """Return the configured reviewer, or None when LLM features are off (UI hides AI buttons)."""
    if provider == "none":
        return None
    raise NotImplementedError(f"LLM provider '{provider}' is not implemented yet")
