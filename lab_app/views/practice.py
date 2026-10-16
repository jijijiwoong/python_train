"""코드 실습: 열린 Day의 문제를 골라 풀거나, 채점 없이 자유롭게 코드를 실행한다."""
import streamlit as st

from lab_app import components as ui
from lab_app.core.progress import exercise_label

FREE = "__free__"

service = ui.get_service()
statuses = service.all_statuses()
exercises = [ex for day, s in statuses.items() if s != "locked" for ex in service.content.lesson(day).exercises]
options = [FREE] + [ex.id for ex in exercises]
labels = {ex.id: exercise_label(ex) for ex in exercises}


def _label(option: str) -> str:
    if option == FREE:
        return "자유 실습 (채점 없음)"
    state = service.exercise_state(option)["status"]
    mark = {"passed": "✅ ", "attempted": "✏️ ", "unsolved": ""}[state]
    return mark + labels[option]


st.title("코드 실습")
target = st.session_state.pop("practice_exercise", None)
if target in options:
    st.session_state["practice_select"] = target
elif st.session_state.get("practice_select") not in options:
    st.session_state["practice_select"] = options[1] if len(options) > 1 else FREE
st.selectbox("문제 선택", options, format_func=_label, key="practice_select")
selected = st.session_state["practice_select"]

if selected == FREE:
    st.caption("수업과 상관없이 자유롭게 코드를 작성하고 실행해 보는 공간입니다. 결과는 채점·기록되지 않습니다.")
    code = ui.editor("editor_free", st.session_state.get("free_code", 'print("Hello, Python!")\n'), min_lines=18)
    st.session_state["free_code"] = code
    stdin = st.text_area("입력값 (input)", key="free_stdin", height=80, help="한 줄에 하나씩, input() 호출 순서대로 입력합니다.")
    if st.button("▶ 실행", type="primary"):
        with st.spinner("실행 중..."):
            st.session_state["free_result"] = service.run(code, stdin)
    if "free_result" in st.session_state:
        st.markdown("##### 실행 결과")
        ui.render_run_result(st.session_state["free_result"])
else:
    ex = service.content.exercise(selected)
    with st.container(border=True):
        ui.exercise_panel(service, ex)
    history = service.submission_history(ex.id, limit=10)
    if history:
        with st.expander(f"이 문제의 제출 기록 ({len(history)}건)"):
            for sub in history:
                result = "✅ 통과" if sub["passed"] else f"❌ {ui.ErrorType(sub['error_type']).label}"
                st.markdown(f"**{sub['submitted_at'][:16].replace('T', ' ')}** · {result} · "
                            f"공개 {sub['public_passed']}/{sub['public_total']} · 숨김 {sub['hidden_passed']}/{sub['hidden_total']}")
                st.code(sub["code"], language="python")
