"""학습 기록: 일자별 이력, 주제별 성취도, 이어하기."""
import pandas as pd
import streamlit as st

from lab_app import components as ui

service = ui.get_service()
stats = service.dashboard_stats()

st.title("학습 기록")

# ---- 이어하기
resume = service.resume_point()
with st.container(border=True):
    if resume is None:
        st.markdown("작성된 수업을 모두 마쳤습니다.")
    else:
        day, section = resume
        lesson = service.content.lesson(day)
        st.markdown(f"**이어서 학습하기** — Day {day}. {lesson.title} · {section + 1}단계 "
                    f"({ui.SECTION_LABELS[lesson.sections[section].type]})")
        if st.button("이어하기", type="primary", icon=":material/play_arrow:"):
            ui.go_to_lesson(day, section)

c1, c2, c3 = st.columns(3)
c1.metric("누적 정답률", ui.percent(stats.accuracy), border=True,
          help=f"통과 {stats.passed_submissions} / 제출 {stats.submissions}")
c2.metric("퀴즈 정답률", ui.percent(stats.quiz_accuracy), border=True,
          help=f"정답 {stats.quiz_correct} / 응답 {stats.quiz_answers}")
c3.metric("완료한 수업", f"{stats.completed_days}일", border=True)

tab_daily, tab_topic, tab_lessons = st.tabs(["일자별 이력", "주제별 성취도", "수업별 진행"])

with tab_daily:
    history = service.daily_history()
    if not history:
        st.caption("아직 학습 기록이 없습니다.")
    else:
        df = pd.DataFrame([{
            "날짜": h["date"], "학습한 Day": ", ".join(f"Day {d}" for d in h["days"]) or "–",
            "제출": h["submissions"], "통과": h["passed"], "실행": h["runs"], "퀴즈": h["quizzes"],
            "완료한 수업": h["lessons_completed"],
        } for h in history])
        st.bar_chart(df.sort_values("날짜"), x="날짜", y=["통과", "제출"], stack=False)
        st.dataframe(df, hide_index=True)

with tab_topic:
    mastery = service.concept_mastery()
    df = pd.DataFrame([{
        "개념": m["label"], "해결한 문제": f"{m['solved']}/{m['exercises']}",
        "해결률": m["solved"] / m["exercises"] if m["exercises"] else 0.0,
        "제출": m["submissions"], "정답률": m["accuracy"],
    } for m in mastery])
    st.dataframe(df, hide_index=True, column_config={
        "해결률": st.column_config.ProgressColumn("해결률", min_value=0.0, max_value=1.0, format="percent"),
        "정답률": st.column_config.NumberColumn("정답률", format="percent"),
    })

with tab_lessons:
    statuses = service.all_statuses()
    for day, status in statuses.items():
        lesson = service.content.lesson(day)
        check = service.checklist(day)
        with st.container(border=True):
            c_info, c_btn = st.columns([4, 1])
            c_info.markdown(f"**Day {day}. {lesson.title}** · {ui.STATUS_LABELS[status]}")
            c_info.caption(f"필수 문제 {len(check.passed_ids)}/{len(check.required_ids)} · "
                           f"정리 퀴즈 {len(check.answered_quiz_ids)}/{len(check.quiz_ids)}")
            if status != "locked" and c_btn.button("열기", key=f"hist_open_{day}", width="stretch"):
                ui.go_to_lesson(day)
