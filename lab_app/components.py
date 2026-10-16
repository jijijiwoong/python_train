"""Shared Streamlit UI pieces. Pages call these; all logic lives in core.progress (LearningService)."""
from __future__ import annotations

import streamlit as st
from code_editor import code_editor

from lab_app import config
from lab_app.core.content import ContentError, ContentRepository
from lab_app.core.errors import ErrorType
from lab_app.core.models import Exercise, GradeResult, Lesson, QuizItem, RunResult, Section
from lab_app.core.progress import LearningService, LockedError

PAGE_DASHBOARD = "views/dashboard.py"
PAGE_LESSON = "views/lesson.py"
PAGE_PRACTICE = "views/practice.py"
PAGE_WRONG_NOTES = "views/wrong_notes.py"
PAGE_HISTORY = "views/history.py"

STATUS_LABELS = {"locked": "🔒 잠김", "not_started": "시작 전", "in_progress": "진행 중", "completed": "✅ 완료"}
SECTION_LABELS = {"review": "복습", "concept": "핵심 개념", "fill_blank": "빈칸 채우기", "coding": "직접 작성", "summary": "정리"}


# ---------------------------------------------------------------- service

@st.cache_resource
def _load_service() -> LearningService:
    return LearningService(ContentRepository())


def get_service() -> LearningService:
    """The shared service; stops the page with a readable message if the content is broken."""
    try:
        return _load_service()
    except ContentError as e:
        st.error("수업 파일(JSON)에 오류가 있어 앱을 시작할 수 없습니다.")
        st.code("\n".join(e.errors), language="text")
        st.stop()


def go_to_lesson(day: int, section: int | None = None) -> None:
    st.session_state["lesson_day"] = day
    if section is not None:
        st.session_state[f"lesson_section_{day}"] = section
    st.switch_page(PAGE_LESSON)


def go_to_practice(exercise_id: str) -> None:
    st.session_state["practice_exercise"] = exercise_id
    st.switch_page(PAGE_PRACTICE)


def percent(value: float | None) -> str:
    return "–" if value is None else f"{value * 100:.0f}%"


# ---------------------------------------------------------------- code editor

def editor(key: str, initial_code: str, min_lines: int = 14) -> str:
    """Syntax-highlighted Python editor. Returns the current code.

    The component reports its text on blur and after a short typing pause, so the
    buttons below always see what is in the editor.
    """
    response = code_editor(
        initial_code, lang="python", theme="default", height=[min_lines, 40], key=key,
        response_mode=["blur", "debounce"], allow_reset=True,
        options={"showLineNumbers": True, "tabSize": 4, "useSoftTabs": True, "wrap": False,
                 "showPrintMargin": False, "fontSize": 15},
    )
    if response and response.get("id"):
        return response.get("text", "")
    return initial_code


# ---------------------------------------------------------------- results

def render_run_result(result: RunResult) -> None:
    label = {"ok": "실행 완료", "error": f"오류: {result.error_type.label}", "timeout": "시간 초과",
             "output_limit": "출력 초과", "internal_error": "실행 도구 오류"}[result.status]
    st.caption(f"{label} · {result.duration_ms} ms")
    if result.stdout:
        st.code(result.stdout, language="text")
    elif result.status == "ok":
        st.caption("(출력 없음)")
    if result.stderr:
        st.code(result.stderr, language="text")
    for i, png in enumerate(result.images, start=1):
        st.image(png, caption=f"그림 {i}")


def render_grade_result(result: GradeResult) -> None:
    counts = f"공개 테스트 {result.public_passed}/{result.public_total}"
    if result.hidden_total:
        counts += f", 숨김 테스트 {result.hidden_passed}/{result.hidden_total}"
    if result.passed:
        st.success(f"정답입니다! {counts} 통과", icon=":material/check_circle:")
    else:
        st.error(f"{result.error_type.label} — {counts} 통과", icon=":material/cancel:")

    for fb in result.feedback:
        text = f"{fb.message}" + (f" ({fb.line}번째 줄)" if fb.line and "줄" not in fb.message else "")
        {"error": st.error, "warning": st.warning}.get(fb.severity, st.info)(text, icon={
            "error": ":material/error:", "warning": ":material/lightbulb:"}.get(fb.severity, ":material/info:"))
    if result.compile_error and result.compile_error.traceback:
        st.code(result.compile_error.traceback, language="text")

    public = [t for t in result.tests if not t.hidden]
    for t in public:
        icon = "✅" if t.passed else "❌"
        with st.expander(f"{icon} 공개 테스트 · {t.description or t.test_id} — {t.message}", expanded=not t.passed):
            if t.expected is not None or t.actual is not None:
                c1, c2 = st.columns(2)
                c1.caption("기대 결과")
                c1.code(t.expected if t.expected not in (None, "") else "(없음)", language="text")
                c2.caption("내 결과")
                c2.code(t.actual if t.actual not in (None, "") else "(출력 없음)", language="text")
            if t.traceback:
                st.code(t.traceback, language="text")
            elif t.stdout and t.expected is None:
                st.caption("출력")
                st.code(t.stdout, language="text")
    hidden = [t for t in result.tests if t.hidden]
    if hidden:
        passed = sum(t.passed for t in hidden)
        failed_types = sorted({t.error_type.label for t in hidden if not t.passed and t.error_type is not ErrorType.NOT_RUN})
        note = f"🔒 숨김 테스트 {passed}/{len(hidden)} 통과"
        if failed_types:
            note += f" · 실패 유형: {', '.join(failed_types)}"
        if passed < len(hidden):
            note += " — 숨김 테스트의 입력값은 공개되지 않습니다. 경계값(0, 음수, 빈 값 등)을 생각해 보세요."
        st.caption(note)


# ---------------------------------------------------------------- exercise workflow

def exercise_panel(service: LearningService, ex: Exercise, *, show_header: bool = True) -> None:
    """Prompt, editor, run/grade buttons, hints and solution for one exercise."""
    key = ex.id
    state = service.exercise_state(ex.id)
    reset_n = st.session_state.get(f"reset_{key}", 0)

    if show_header:
        badge = {"passed": "✅ 통과", "attempted": f"시도 {state['attempts']}회", "unsolved": "미해결"}[state["status"]]
        kind = "빈칸 채우기" if ex.kind == "fill_blank" else "코드 작성"
        optional = "" if ex.required else " · 도전(선택)"
        st.markdown(f"#### {ex.title}")
        st.caption(f"{kind}{optional} · 난이도 {'★' * ex.difficulty}{'☆' * (3 - ex.difficulty)} · {badge}")
    st.markdown(ex.prompt_md)
    if ex.entry_mode == "function":
        st.caption(f"채점 방식: 함수 `{ex.function_name}()`를 여러 입력으로 호출해 반환값을 확인합니다.")

    code = editor(f"editor_{key}_{reset_n}", service.current_code(ex.id))

    stdin = ""
    if ex.entry_mode == "program":
        sample = next((t.stdin for t in ex.public_tests if t.stdin), "")
        with st.expander("실행할 때 넣을 입력값 (input)", expanded=bool(sample)):
            stdin = st.text_area("입력값", value=sample, key=f"stdin_{key}", height=80,
                                 label_visibility="collapsed", help="한 줄에 하나씩, input() 호출 순서대로 입력합니다.")

    c_run, c_grade, c_hint, c_reset = st.columns([1, 1, 1, 1])
    run_clicked = c_run.button("▶ 실행", key=f"run_{key}", width="stretch")
    grade_clicked = c_grade.button("✔ 채점", key=f"grade_{key}", type="primary", width="stretch")
    hints_open = state["hints_revealed"]
    hint_clicked = c_hint.button(f"💡 힌트 ({hints_open}/{len(ex.hints)})", key=f"hint_{key}",
                                 disabled=hints_open >= len(ex.hints), width="stretch")
    reset_clicked = c_reset.button("↺ 처음 코드로", key=f"reset_btn_{key}", width="stretch")

    if reset_clicked:
        service.save_draft(ex.id, ex.starter_code)
        st.session_state[f"reset_{key}"] = reset_n + 1
        st.session_state.pop(f"result_{key}", None)
        st.rerun()
    if hint_clicked:
        service.reveal_next_hint(ex.id)
        st.rerun()
    if run_clicked:
        with st.spinner("실행 중..."):
            st.session_state[f"result_{key}"] = ("run", service.run(code, stdin, exercise_id=ex.id))
    if grade_clicked:
        with st.spinner("채점 중..."):
            try:
                outcome = service.submit(ex.id, code)
            except LockedError as e:
                st.warning(str(e))
            else:
                st.session_state[f"result_{key}"] = ("grade", outcome.result)
                if outcome.lesson_completed:
                    st.session_state["just_completed"] = ex.day
                st.rerun()  # refresh badges, hint counts and the solution button

    for i, hint in enumerate(service.revealed_hints(ex.id), start=1):
        st.info(f"**힌트 {i}.** {hint}", icon=":material/lightbulb:")

    stored = st.session_state.get(f"result_{key}")
    if stored:
        kind, result = stored
        st.markdown("##### 실행 결과" if kind == "run" else "##### 채점 결과")
        render_run_result(result) if kind == "run" else render_grade_result(result)

    _solution_box(service, ex)


def _solution_box(service: LearningService, ex: Exercise) -> None:
    key = f"solution_{ex.id}"
    state = service.exercise_state(ex.id)
    if state["solution_viewed"]:
        with st.expander("📖 모범 답안", expanded=False):
            st.code(ex.solution, language="python")
        return
    if not service.can_view_solution(ex.id):
        st.caption(f"📖 모범 답안은 {config.SOLUTION_UNLOCK_ATTEMPTS}번 이상 채점한 뒤에 볼 수 있습니다.")
        return
    if st.session_state.get(key) != "confirm":
        if st.button("📖 모범 답안 보기", key=f"{key}_ask"):
            st.session_state[key] = "confirm"
            st.rerun()
        return
    st.warning("모범 답안을 보면 기록에 '정답 열람'으로 남습니다. 그래도 볼까요?")
    c1, c2 = st.columns(2)
    if c1.button("네, 볼게요", key=f"{key}_yes", type="primary"):
        service.view_solution(ex.id)
        st.session_state.pop(key, None)
        st.rerun()
    if c2.button("조금 더 생각해 볼게요", key=f"{key}_no"):
        st.session_state.pop(key, None)
        st.rerun()


# ---------------------------------------------------------------- lesson content

def render_blocks(service: LearningService, day: int, section: Section) -> None:
    for i, block in enumerate(section.blocks):
        if block.kind == "text":
            st.markdown(block.md)
        elif block.kind == "tip":
            st.info(block.md, icon=":material/tips_and_updates:")
        elif block.kind == "code":
            st.code(block.code, language="python")
            if block.runnable:
                key = f"block_{day}_{i}"
                if st.button("▶ 예제 실행", key=key):
                    st.session_state[f"{key}_out"] = service.run(block.code, timeout=block.time_limit_sec)
                out = st.session_state.get(f"{key}_out")
                if out is not None:
                    render_run_result(out)


def quiz_item(service: LearningService, day: int, quiz: QuizItem, answers: dict) -> None:
    st.markdown(quiz.question_md)
    prev = answers.get(quiz.id)
    choice = st.radio("선택", options=list(range(len(quiz.choices))), format_func=lambda i: quiz.choices[i],
                      index=prev["selected"] if prev else None, key=f"quiz_{quiz.id}", label_visibility="collapsed")
    if st.button("답 제출", key=f"quiz_submit_{quiz.id}", disabled=choice is None):
        service.answer_quiz(day, quiz.id, choice)
        st.rerun()
    if prev:
        if prev["correct"]:
            st.success("정답입니다.", icon=":material/check_circle:")
        else:
            st.error("오답입니다. 다시 골라 제출할 수 있어요.", icon=":material/cancel:")
            st.markdown(f"**정답:** {quiz.choices[quiz.answer_index]}")
        st.caption("해설")
        st.markdown(quiz.explanation_md)


def lesson_status_line(service: LearningService, lesson: Lesson) -> None:
    check = service.checklist(lesson.day)
    parts = [f"필수 문제 {len(check.passed_ids)}/{len(check.required_ids)}",
             f"정리 퀴즈 {len(check.answered_quiz_ids)}/{len(check.quiz_ids)}"]
    st.caption("완료 조건: " + " · ".join(parts) + (" — ✅ 완료" if check.completed else ""))
