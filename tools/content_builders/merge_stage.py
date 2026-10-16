"""Copy built lessons into lab_app/content and register them in curriculum.json with a minimal, format-preserving diff.

usage: python merge_stage.py <project_root> <built_dir> <meta_module> <first_day> <last_day>
"""
import importlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
root, built, meta_name, first, last = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
meta = importlib.import_module(meta_name)

for d in range(first, last + 1):
    shutil.copy(built / "lessons" / f"day{d:02d}.json", root / "lab_app" / "content" / "lessons" / f"day{d:02d}.json")

p = root / "lab_app" / "content" / "curriculum.json"
s = p.read_text(encoding="utf-8")
cur = json.loads(s)
lines = s.split("\n")

# concepts: insert after the last concept entry
new_concepts = [(k, v) for k, v in meta.NEW_CONCEPTS.items() if k not in cur["concepts"]]
if new_concepts:
    last_key = list(cur["concepts"])[-1]
    idx = next(i for i, l in enumerate(lines) if l.strip().startswith(json.dumps(last_key, ensure_ascii=False) + ":"))
    lines[idx] = lines[idx].rstrip(",") + ","
    add = [f"    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in new_concepts]
    lines[idx + 1:idx + 1] = [l + "," for l in add[:-1]] + [add[-1]]

# days: insert after the last day entry
have = {d["day"] for d in cur["days"]}
new_days = [{"day": d, "title": t, "file": f"lessons/day{d:02d}.json", "is_review": d % 7 == 0}
            for d, t in meta.DAYS if first <= d <= last and d not in have]
if new_days:
    idx = max(i for i, l in enumerate(lines) if l.strip().startswith('{"day":'))
    lines[idx] = lines[idx].rstrip(",") + ","
    add = ["    " + json.dumps(d, ensure_ascii=False) for d in new_days]
    lines[idx + 1:idx + 1] = [l + "," for l in add[:-1]] + [add[-1]]

out = "\n".join(lines)
check = json.loads(out)
p.write_text(out, encoding="utf-8", newline="\n")
print(f"concepts +{len(new_concepts)} -> {len(check['concepts'])}, days +{len(new_days)} -> {len(check['days'])}")
