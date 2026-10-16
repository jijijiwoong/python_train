"""Shared helpers for scratch lesson builders. The JSON files written to lab_app/content are the source of truth."""
import json
from pathlib import Path
from textwrap import dedent


def c(s: str) -> str:
    return dedent(s).lstrip("\n")


def quiz(qid, q, choices, ans, exp):
    return {"id": qid, "question_md": q, "choices": choices, "answer_index": ans, "explanation_md": exp}


def text(md):
    return {"kind": "text", "md": md}


def tip(md):
    return {"kind": "tip", "md": md}


def code(src, out=None):
    b = {"kind": "code", "code": c(src), "runnable": out is not None}
    if out is not None:
        b["expected_output"] = out
    return b


def t(tid, stdin=None, out=None, args=None, ret=..., raises=None, desc="", compare=None, kwargs=None):
    d = {"id": tid, "hidden": tid.startswith("h"), "description": desc}
    if stdin is not None:
        d["stdin"] = stdin
    if args is not None or kwargs is not None:
        d["call"] = {"args": args or []}
        if kwargs:
            d["call"]["kwargs"] = kwargs
    expect = {}
    if out is not None:
        expect["stdout"] = out
    if ret is not ...:
        expect["return"] = ret
    if raises:
        expect["raises"] = raises
    d["expect"] = expect
    if compare:
        d["compare"] = compare
    return d


def lines(*xs):
    return "".join(f"{x}\n" for x in xs)


def ex(id_, kind, title, prompt, concepts, difficulty, starter, tests, hints, solution, mode="program",
       name=None, checks=None, required=True, time_limit=None):
    e = {"id": id_, "kind": kind, "title": title, "prompt_md": prompt, "concepts": concepts,
         "difficulty": difficulty, "required": required, "starter_code": c(starter),
         "entry": {"mode": mode, **({"name": name} if name else {})}, "tests": tests, "hints": hints,
         "solution": c(solution)}
    if checks:
        e["checks"] = checks
    if time_limit:
        e["time_limit_sec"] = time_limit
    return e


def lesson(day, title, week, concepts, objectives, review, concept, fill_intro, coding_intro, summary, exercises,
           stage="basics", is_review=False):
    fills = [e["id"] for e in exercises if e["kind"] == "fill_blank"]
    codes = [e["id"] for e in exercises if e["kind"] == "coding"]
    return {
        "schema_version": 1, "day": day, "title": title, "stage": stage, "week": week, "is_review": is_review,
        "objectives": objectives, "concepts": concepts,
        "sections": [
            {"type": "review", "minutes": 2, **review},
            {"type": "concept", "minutes": 4, **concept},
            {"type": "fill_blank", "minutes": 3, "title": "빈칸 채우기", "intro_md": fill_intro, "exercise_ids": fills},
            {"type": "coding", "minutes": 4, "title": "직접 작성하기", "intro_md": coding_intro, "exercise_ids": codes},
            {"type": "summary", "minutes": 2, **summary},
        ],
        "exercises": exercises,
    }


def write_lessons(out_dir: Path, lessons: list[dict]) -> None:
    (out_dir / "lessons").mkdir(parents=True, exist_ok=True)
    for d in lessons:
        path = out_dir / "lessons" / f"day{d['day']:02d}.json"
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name)


# ---------------------------------------------------------------- automatic tidy-ups applied by write_lessons
import re as _re

_BOLD_PAREN = _re.compile(r"\*\*([^*\n]+?)\(([^()\n]*)\)\*\*")
_CODE_KEYS = {"code", "starter_code", "solution", "expected_output", "stdin", "stdout", "call", "expect", "entry", "checks"}
_CALL = _re.compile(r"^(\s*)(.*?\b[\w.]+)\((.+)\)(:?)$")


def _fix_bold(value):
    """`**용어(설명)**조사` does not render in CommonMark; move the parenthesis out: `**용어**(설명)조사`."""
    return _BOLD_PAREN.sub(r"**\1**(\2)", value)


def _wrap_long_lines(src, limit=100):
    out = []
    for line in src.split("\n"):
        m = _CALL.match(line)
        if len(line) > limit and m and line.count("(") == line.count(")"):
            indent, head, args, colon = m.groups()
            out.append(f"{indent}{head}(")
            out.append(f"{indent}    {args}")
            out.append(f"{indent}){colon}")
        else:
            out.append(line)
    return "\n".join(out)


def _tidy(node, key=None):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("solution", "starter_code", "code") and isinstance(v, str):
                node[k] = _wrap_long_lines(v)
            elif k not in _CODE_KEYS:
                node[k] = _tidy(v, k)
        return node
    if isinstance(node, list):
        return [_tidy(v, key) for v in node]
    if isinstance(node, str):
        return _fix_bold(node)
    return node


_write_lessons_raw = write_lessons


def write_lessons(out_dir, lessons):  # noqa: F811 - wraps the plain writer with tidy-ups
    _write_lessons_raw(out_dir, [_tidy(d) for d in lessons])


# ---------------------------------------------------------------- token-based wrapper (replaces _wrap_long_lines)
import io as _io
import tokenize as _tokenize

_PAIRS = {")": "(", "]": "[", "}": "{"}


def _wrap_line(line, limit=100):
    if len(line) <= limit:
        return [line]
    indent = line[: len(line) - len(line.lstrip())]
    try:
        toks = list(_tokenize.generate_tokens(_io.StringIO(line.strip() + "\n").readline))
    except (_tokenize.TokenError, SyntaxError, IndentationError):
        return [line]
    base = len(indent)
    stack, pairs, fdepth = [], {}, 0
    commas = []
    for tok in toks:
        if tok.type == _tokenize.FSTRING_START:
            fdepth += 1
        elif tok.type == _tokenize.FSTRING_END:
            fdepth -= 1
        elif tok.type == _tokenize.OP and fdepth == 0:
            col = base + tok.start[1]
            if tok.string in "([{":
                stack.append(col)
            elif tok.string in ")]}":
                if not stack:
                    return [line]
                pairs[stack.pop()] = col
            elif tok.string == "," and len(stack) == 1:
                commas.append((stack[0], col))
    body = line.rstrip()
    tail = ":" if body.endswith(":") else ""
    last = len(body) - len(tail) - 1
    opener = next((o for o, c in pairs.items() if c == last), None)
    if opener is None or last - opener < 2:
        return [line]
    cuts = [c for o, c in commas if o == opener]
    parts, start = [], opener + 1
    for c in cuts:
        parts.append(line[start:c].strip())
        start = c + 1
    parts.append(line[start:last].strip())
    parts = [p for p in parts if p]
    out = [line[: opener + 1]]
    for p in parts:
        out += _wrap_line(f"{indent}    {p},", limit) if len(parts) > 1 else _wrap_line(f"{indent}    {p}", limit)
    out.append(f"{indent}{line[last]}{tail}")
    return out


def _wrap_long_lines(src, limit=100):  # noqa: F811
    wrapped = "\n".join(piece for line in src.split("\n") for piece in _wrap_line(line, limit))
    try:
        compile(wrapped, "<wrap>", "exec")
    except SyntaxError:
        return src
    return wrapped
