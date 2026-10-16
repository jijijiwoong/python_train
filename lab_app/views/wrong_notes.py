"""오답 노트: 틀린 문제·제출 코드·오류 유형, 재도전, 반복 실수 통계."""
import pandas as pd
import streamlit as st

from lab_app import components as ui
from lab_app.core.errors import hint_for

service = ui.get_service()

st.title("오답 노트")
open_notes = service.wrong_notes(resolved=False)
done_notes = service.wrong_notes(resolved=True)
error_stats = service.error_stats()

c1, c2, c3 = st.columns(3)
c1.metric("미해결 오답", f"{len(open_notes)}개", border=True)
c2.metric("해결한 오답", f"{len(done_notes)}개", border=True)
c3.metric("가장 잦은 실수", error_stats[0][0].label if error_stats else "–", border=True)

tab_open, tab_done, tab_stats = st.tabs([f"미해결 ({len(open_notes)})", f"해결됨 ({len(done_notes)})", "반복 실수 통계"])


def render_note(note: dict, resolved: bool) -> None:
    concepts = ", ".join(service.content.curriculum.concept_label(t) for t in note["concepts"])
    title = f"Day {note['day']} · {note['title']} — {note['error_type'].label} · {note['wrong_count']}회 틀림"
    with st.expander(("✅ " if resolved else "❌ ") + title):
        st.caption(f"개념: {concepts or '–'} · 마지막으로 틀린 시각: {note['last_wrong_at'][:16].replace('T', ' ')}")
        st.markdown("**마지막으로 틀린 코드**")
        st.code(note["last_wrong_code"], language="python")
        if tip := hint_for(note["error_type"]):
            st.info(tip, icon=":material/lightbulb:")
        memo = st.text_area("메모 (왜 틀렸는지 적어 두면 복습에 도움이 됩니다)", value=note["memo"],
                            key=f"memo_{note['exercise_id']}", height=80)
        c_save, c_retry = st.columns([1, 1])
        if c_save.button("메모 저장", key=f"memo_save_{note['exercise_id']}", width="stretch"):
            service.set_memo(note["exercise_id"], memo)
            st.toast("메모를 저장했습니다.")
        if c_retry.button("다시 풀기", key=f"retry_{note['exercise_id']}", type="primary", width="stretch"):
            ui.go_to_practice(note["exercise_id"])


with tab_open:
    if not open_notes:
        st.caption("미해결 오답이 없습니다.")
    for note in open_notes:
        render_note(note, resolved=False)

with tab_done:
    if not done_notes:
        st.caption("아직 해결한 오답이 없습니다.")
    for note in done_notes:
        render_note(note, resolved=True)

with tab_stats:
    if not error_stats:
        st.caption("아직 통계가 없습니다.")
    else:
        df = pd.DataFrame({"오류 유형": [et.label for et, _ in error_stats], "횟수": [n for _, n in error_stats]})
        st.bar_chart(df, x="오류 유형", y="횟수", horizontal=True, sort="-횟수")
        st.dataframe(df, hide_index=True)
