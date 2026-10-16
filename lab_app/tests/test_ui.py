"""UI smoke tests with Streamlit AppTest: every screen renders and the main flows are wired to the service.

The code editor is a custom component that AppTest cannot type into, so tests set the
editor's starting code through the service (draft code) and then press the real buttons.
"""
from pathlib import Path

import pytest
from streamlit import config as st_config
from streamlit.testing.v1 import AppTest

from lab_app import components, config
from lab_app.core.content import ContentRepository
from lab_app.core.progress import LearningService
from lab_app.tests.conftest import write_content

APP = Path(__file__).resolve().parents[1] / "app.py"
PAGES = ["views/dashboard.py", "views/lesson.py", "views/practice.py", "views/wrong_notes.py", "views/history.py"]


@pytest.fixture
def ui_db(tmp_path, monkeypatch) -> Path:
    """Point the app at a temporary DB and the real content; allow the localhost guard to pass."""
    db = tmp_path / "ui.db"
    monkeypatch.setattr(config, "DB_PATH", db)
    previous = st_config.get_option("server.address")
    st_config.set_option("server.address", "localhost")
    components._load_service.clear()
    yield db
    components._load_service.clear()
    st_config.set_option("server.address", previous)


@pytest.fixture
def service(ui_db) -> LearningService:
    """A second service on the same DB, used to seed state the UI should show."""
    return LearningService(ContentRepository(), ui_db)


def run_app(page: str | None = None) -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    if page:
        at.switch_page(page).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def texts(elements) -> str:
    return "\n".join(str(e.value) for e in elements)


# ---------------------------------------------------------------- app shell

@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_on_a_fresh_db(ui_db, page):
    at = run_app(page)
    assert at.title, "page has no title"
    assert "연속 0일" in texts(at.sidebar.caption)


def test_guard_blocks_non_local_address(ui_db):
    st_config.set_option("server.address", "0.0.0.0")
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert "이 PC에서만" in texts(at.error)
    assert not at.title  # nothing else rendered


def test_broken_content_shows_readable_error(ui_db, tmp_path, monkeypatch, lesson_dicts):
    lesson_dicts[1]["sections"].reverse()
    monkeypatch.setattr(config, "CONTENT_DIR", write_content(tmp_path / "bad", lessons=lesson_dicts))
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert "수업 파일(JSON)에 오류" in texts(at.error)
    assert "섹션 순서" in texts(at.code)


# ---------------------------------------------------------------- dashboard & lesson

def test_dashboard_start_button_opens_todays_lesson(ui_db):
    at = run_app()
    next(b for b in at.button if b.label == "학습 시작").click().run()
    assert at.title[0].value.startswith("Day 1.")


def test_only_unlocked_days_are_selectable(ui_db, service):
    at = run_app("views/lesson.py")
    options = at.selectbox[0].options
    assert len(options) == 1 and options[0].startswith("Day 1")


def test_concept_example_runs_in_ui(ui_db):
    at = run_app("views/lesson.py")
    at.radio[0].set_value(1).run()
    at.button(key="block_1_1").click().run()
    assert "Hello, Python!" in texts(at.code)


def test_grading_from_lesson_page(ui_db, service):
    ex = service.content.exercise("d01_fill_1")
    service.save_draft(ex.id, ex.solution)  # what the editor will show
    at = run_app("views/lesson.py")
    at.radio[0].set_value(2).run()
    at.button(key=f"grade_{ex.id}").click().run()
    assert "정답입니다" in texts(at.success)
    assert service.exercise_state(ex.id)["status"] == "passed"


def test_wrong_answer_hint_and_solution_flow(ui_db, service):
    ex = service.content.exercise("d01_code_1")
    at = run_app("views/lesson.py")
    at.radio[0].set_value(3).run()
    assert "1번 이상 채점한 뒤에" in texts(at.caption)            # solution locked before any submission

    at.button(key=f"grade_{ex.id}").click().run()                 # starter code → wrong
    assert "오답" in texts(at.error)
    at.button(key=f"hint_{ex.id}").click().run()
    assert ex.hints[0] in texts(at.info)

    at.button(key=f"solution_{ex.id}_ask").click().run()
    assert "정답 열람" in texts(at.warning)                         # confirmation step
    at.button(key=f"solution_{ex.id}_yes").click().run()
    assert ex.solution.strip() in texts(at.code)
    assert service.exercise_state(ex.id)["solution_viewed"] is True


def test_summary_quiz_completes_lesson_after_exercises(ui_db, service):
    for ex_id in ("d01_fill_1", "d01_code_1"):
        service.submit(ex_id, service.content.exercise(ex_id).solution)
    at = run_app("views/lesson.py")
    at.radio[0].set_value(4).run()
    assert "정리 퀴즈 제출" in texts(at.warning)
    for qid in service.content.lesson(1).summary_quiz_ids:
        at.radio(key=f"quiz_{qid}").set_value(0).run()
        at.button(key=f"quiz_submit_{qid}").click().run()
    assert "오늘 수업을 완료했습니다" in texts(at.success)
    assert service.lesson_status(1) == "completed"
    assert any(b.label == "Day 2 수업으로" for b in at.button)


# ---------------------------------------------------------------- practice, wrong notes, history

def test_free_practice_run(ui_db):
    at = run_app("views/practice.py")
    at.selectbox(key="practice_select").set_value("__free__").run()
    next(b for b in at.button if b.label == "▶ 실행").click().run()
    assert "Hello, Python!" in texts(at.code)


def test_wrong_note_retry_opens_practice(ui_db, service):
    service.submit("d01_code_1", "print(n)\n")
    at = run_app("views/wrong_notes.py")
    assert any("총액 계산하기" in e.label for e in at.expander)
    assert any(m.value == "1개" for m in at.metric)
    at.button(key="retry_d01_code_1").click().run()
    assert at.title[0].value == "코드 실습"
    assert at.selectbox(key="practice_select").value == "d01_code_1"


def test_history_shows_records_and_resume(ui_db, service):
    service.view_section(1, 2)
    service.submit("d01_fill_1", 'print("hello")\n')
    at = run_app("views/history.py")
    assert at.dataframe, "daily history table missing"
    assert "3단계" in texts(at.markdown)
    next(b for b in at.button if b.label == "이어하기").click().run()
    assert at.title[0].value.startswith("Day 1.")
    assert at.radio[0].value == 2
