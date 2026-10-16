"""Validate built lessons on a temp copy of lab_app/content (never touches the real content).

usage: python validate_any.py <project_root> <built_dir> <first_day> <last_day>
Merges concepts/days from every stage*_meta.py in this folder.
"""
import importlib
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
root, built, first, last = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, str(root))

from lab_app.core.content import ContentRepository  # noqa: E402
from lab_app.core.grader import verify_lesson  # noqa: E402

concepts, days = {}, []
for meta_file in sorted(HERE.glob("stage*_meta.py")):
    m = importlib.import_module(meta_file.stem)
    concepts.update(m.NEW_CONCEPTS)
    days += [(d, t) for d, t in m.DAYS]

tmp = Path(tempfile.mkdtemp(prefix="stage_"))
shutil.copytree(root / "lab_app" / "content", tmp / "content")
for f in (built / "lessons").glob("day*.json"):
    shutil.copy(f, tmp / "content" / "lessons" / f.name)
cur = json.loads((tmp / "content" / "curriculum.json").read_text(encoding="utf-8"))
cur["concepts"].update({k: v for k, v in concepts.items() if k not in cur["concepts"]})
have = {d["day"] for d in cur["days"]}
cur["days"] += [{"day": d, "title": t, "file": f"lessons/day{d:02d}.json", "is_review": d % 7 == 0}
                for d, t in sorted(days) if d not in have and d <= last]
(tmp / "content" / "curriculum.json").write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")

repo = ContentRepository(tmp / "content")
print("days:", repo.available_days[0], "..", repo.available_days[-1], "| warnings:", repo.warnings or "none")
bad = 0
for day in range(first, last + 1):
    start = time.perf_counter()
    problems = verify_lesson(repo.lesson(day))
    print(day, repo.lesson(day).title, f"({time.perf_counter() - start:.0f}s)", "OK" if not problems else problems, flush=True)
    bad += bool(problems)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad or repo.warnings else 0)
