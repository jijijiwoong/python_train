"""Compact helpers for stage-4 (PyTorch) builders: expected values come from running each solution here."""
import copy
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import c, ex, lesson, quiz, text, tip, t, write_lessons  # noqa: E402,F401
from cb_data import ncode  # noqa: E402

ST, TL = "dl", 60


def plain(x):
    if isinstance(x, bool) or x is None or isinstance(x, (int, float, str)):
        return x
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    return plain(x.tolist())


def call(sol, name, args):
    ns = {"__name__": "__sol__"}
    exec(compile(sol, "<sol>", "exec"), ns)
    return plain(ns[name](*copy.deepcopy(args)))


def X(id_, title, prompt, concepts, diff, solution, name, cases, hints, blanks=None, starter=None, tol=1e-4,
      checks=None, required=True, tl=TL):
    """cases: list of arg-lists (or (args, desc)); first is public t1, rest hidden h1, h2..."""
    sol = c(solution)
    if starter is None:
        if blanks:
            starter = sol
            for b in blanks:
                assert b in starter, (id_, b)
                starter = starter.replace(b, "____", 1)
        else:
            lines = sol.split("\n")
            i = next(i for i, l in enumerate(lines) if l.startswith(f"def {name}("))
            starter = "\n".join(lines[: i + 1]) + "\n    # 여기에 코드를 작성하세요\n    pass\n"
    tests = []
    for j, case in enumerate(cases):
        args, desc = case if isinstance(case, tuple) else (case, "")
        extra = {"compare": {"mode": "float", "tol": tol}} if tol else {}
        ret = call(sol, name, args)
        if os.environ.get("DLDEBUG"):
            print("  ", id_, args if len(str(args)) < 60 else "...", "->", str(ret)[:150])
        tests.append(t("t1" if j == 0 else f"h{j}", args=args, ret=ret,
                       desc=desc or ("기본" if j == 0 else ""), **extra))
    return ex(id_, "fill_blank" if blanks else "coding", title, prompt, concepts, diff, starter, tests, hints, sol,
              mode="function", name=name, checks=checks, required=required, time_limit=tl)


def D(day, title, week, concepts, objectives, review_md, review_q, concept_title, concept_md, example, tip_md,
      fill_intro, coding_intro, points, summary_qs, exercises, review_title="어제 배운 내용 떠올리기", extra_blocks=()):
    """review_q / summary_qs: (question, choices, answer_index) tuples."""
    blocks = [text(concept_md), ncode(example, TL)] + list(extra_blocks)
    if tip_md:
        blocks.append(tip(tip_md))
    return lesson(
        day, title, week, concepts, objectives,
        review={"title": review_title, "content_md": review_md,
                "quiz": [quiz(f"d{day}_review_q{i + 1}", q, ch, a, "") for i, (q, ch, a) in enumerate(review_q)]},
        concept={"title": concept_title, "blocks": blocks},
        fill_intro=fill_intro, coding_intro=coding_intro,
        summary={"title": "오늘의 핵심 정리" if day % 7 else "마무리", "points": points,
                 "quiz": [quiz(f"d{day}_summary_q{i + 1}", q, ch, a, "") for i, (q, ch, a) in enumerate(summary_qs)]},
        exercises=exercises, stage=ST, is_review=day % 7 == 0)
