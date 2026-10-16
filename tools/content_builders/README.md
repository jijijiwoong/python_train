# content_builders

These scripts generated the lesson JSON (`lab_app/content/lessons/dayNN.json`). The **JSON files are the source of truth**. The app and the tests do not use these scripts.

| File | Role |
|---|---|
| `build_content.py` | Day 1–7 |
| `build_week3.py` ~ `build_week24.py` | One week (7 days) each. Week 2 (Day 8–14) was built in a separate session and has no builder |
| `cb_common.py`, `cb_data.py`, `dl_common.py` | Shared helpers (lesson structure, example-output capture, auto-computed expected values for stage 4) |
| `stage_meta.py`, `stage2~4_meta.py` | New concept tags and day titles for each stage |
| `validate_any.py` | Validates built results on a temporary copy (the real content is untouched) |
| `merge_stage.py` | Merges built results into `lab_app/content` (adds only the needed lines to `curriculum.json`) |

Usage (from the project folder):

```powershell
.venv\Scripts\python -X utf8 tools\content_builders\build_week18.py $env:TEMP\built
.venv\Scripts\python -X utf8 tools\content_builders\validate_any.py . $env:TEMP\built 120 126
```

- Note: if you edit the JSON directly and then rerun a builder, your edits are overwritten.
- Stage 3–4 expected values depend on the library versions (torch 2.14.1+cpu, scikit-learn 1.9.1).
