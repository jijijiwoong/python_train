"""오늘의 수업: 복습 → 개념 → 빈칸 채우기 → 직접 작성 → 정리 (15분)."""
import streamlit as st

from lab_app import components as ui

service = ui.get_service()
statuses = service.all_statuses()
open_days = [d for d, s in statuses.items() if s != "locked"]

if not open_days:
    st.title("오늘의 수업")
    st.info("아직 수업이 없습니다.")
    st.stop()

default_day = st.session_state.get("lesson_day") or service.today_day() or open_days[-1]
if default_day not in open_days:
    default_day = open_days[0]

top_left, top_right = st.columns([3, 1])
with top_right:
    day = st.selectbox("수업 선택", open_days, index=open_days.index(default_day),
                       format_func=lambda d: f"Day {d} · {ui.STATUS_LABELS[statuses[d]]}")
st.session_state["lesson_day"] = day
lesson = service.content.lesson(day)
if statuses[day] == "not_started":
    service.start_lesson(day)
with top_left:
    st.title(f"Day {lesson.day}. {lesson.title}")
    st.caption(" · ".join(filter(None, [lesson.is_review and "누적 복습", f"{lesson.week}주차", "약 15분"])))

ui.lesson_status_line(service, lesson)
if st.session_state.pop("just_completed", None) == day:
    st.success(f"🎉 Day {day} 수업을 완료했습니다! 다음 수업이 열렸습니다.")

# ---- section stepper (index stored for "이어하기")
section_key = f"lesson_section_{day}"
if section_key not in st.session_state:
    row_section = service.resume_point()
    st.session_state[section_key] = row_section[1] if row_section and row_section[0] == day else 0


def _remember_section() -> None:
    service.view_section(day, st.session_state[section_key])


def _move(delta: int) -> None:
    st.session_state[section_key] = max(0, min(len(lesson.sections) - 1, st.session_state[section_key] + delta))
    _remember_section()


st.radio("단계", options=list(range(len(lesson.sections))), key=section_key, horizontal=True, on_change=_remember_section,
         format_func=lambda i: f"{i + 1}. {ui.SECTION_LABELS[lesson.sections[i].type]} · {lesson.sections[i].minutes}분",
         label_visibility="collapsed")
index = st.session_state[section_key]
section = lesson.sections[index]
st.divider()
st.header(section.title or ui.SECTION_LABELS[section.type])

if section.type == "review":
    st.markdown(section.content_md)
    if index == 0 and lesson.objectives:
        with st.expander("오늘의 학습 목표", expanded=True):
            st.markdown("\n".join(f"- {o}" for o in lesson.objectives))
    answers = service.quiz_answers(day)
    for quiz in section.quiz:
        with st.container(border=True):
            ui.quiz_item(service, day, quiz, answers)

elif section.type == "concept":
    ui.render_blocks(service, day, section)

elif section.type in ("fill_blank", "coding"):
    if section.intro_md:
        st.markdown(section.intro_md)
    for ex_id in section.exercise_ids:
        with st.container(border=True):
            ui.exercise_panel(service, lesson.exercise(ex_id))

elif section.type == "summary":
    st.markdown("\n".join(f"- {p}" for p in section.points))
    answers = service.quiz_answers(day)
    st.subheader("점검 퀴즈")
    for quiz in section.quiz:
        with st.container(border=True):
            ui.quiz_item(service, day, quiz, answers)
    check = service.checklist(day)
    if check.completed:
        st.success("오늘 수업을 완료했습니다. 수고하셨어요!")
        nxt = next((d for d in service.content.available_days if d > day), None)
        if nxt is not None and st.button(f"Day {nxt} 수업으로", type="primary"):
            ui.go_to_lesson(nxt, 0)
    else:
        missing = [lesson.exercise(e).title for e in check.remaining_exercises]
        msg = "수업을 완료하려면: "
        msg += " / ".join(filter(None, [missing and f"필수 문제 통과 ({', '.join(missing)})",
                                        check.remaining_quizzes and "정리 퀴즈 제출"]))
        st.warning(msg)

st.divider()
prev_col, _, next_col = st.columns([1, 3, 1])
prev_col.button("← 이전 단계", on_click=_move, args=(-1,), disabled=index == 0, width="stretch")
next_col.button("다음 단계 →", on_click=_move, args=(1,), disabled=index == len(lesson.sections) - 1,
                type="primary", width="stretch")
