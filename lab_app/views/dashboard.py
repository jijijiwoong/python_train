"""대시보드: 오늘의 수업, 학습 지표, 취약 개념과 복습 추천."""
import streamlit as st

from lab_app import components as ui

service = ui.get_service()
stats = service.dashboard_stats()
curriculum = service.content.curriculum

st.title("대시보드")

# ---- 오늘의 수업
with st.container(border=True):
    if stats.today_day is None:
        st.subheader("작성된 수업을 모두 마쳤습니다 🎉")
        st.write("다음 수업이 준비되면 여기에 표시됩니다. 그동안 오답 노트로 복습해 보세요.")
    else:
        lesson = service.content.lesson(stats.today_day)
        status = service.lesson_status(lesson.day)
        stage = curriculum.stage_of(lesson.day)
        st.caption(f"오늘의 수업 · {stage.title if stage else ''} · {lesson.week}주차")
        st.subheader(f"Day {lesson.day}. {lesson.title}")
        st.markdown("\n".join(f"- {o}" for o in lesson.objectives))
        ui.lesson_status_line(service, lesson)
        label = "이어서 학습하기" if status == "in_progress" else "학습 시작"
        if st.button(label, type="primary", icon=":material/play_arrow:"):
            service.start_lesson(lesson.day)
            resume = service.resume_point()
            section = resume[1] if resume and resume[0] == lesson.day else 0
            ui.go_to_lesson(lesson.day, section)

# ---- 지표
c1, c2, c3, c4 = st.columns(4)
c1.metric("학습 일수", f"{stats.study_days}일", border=True, help="문제를 제출하거나 퀴즈를 푼 날만 셉니다.")
c2.metric("연속 학습", f"{stats.streak}일", border=True, help="오늘 아직 공부하지 않았다면 어제까지의 기록입니다.")
c3.metric("커리큘럼 진행률", ui.percent(stats.curriculum_progress), border=True,
          help=f"완료 {stats.completed_days}일 / 전체 {stats.total_days}일 (작성된 수업 {stats.authored_days}일)")
c4.metric("누적 정답률", ui.percent(stats.accuracy), border=True,
          help=f"통과한 제출 {stats.passed_submissions} / 전체 제출 {stats.submissions}")

# ---- 단계별 진행
st.subheader("커리큘럼")
statuses = service.all_statuses()
for stage in curriculum.stages:
    start, end = stage.day_range
    done = sum(1 for d, s in statuses.items() if start <= d <= end and s == "completed")
    total = end - start + 1
    st.progress(done / total, text=f"{stage.order}단계 · {stage.title} — {done}/{total}일 ({stage.weeks}주)")

week_days = [d for d in service.content.available_days]
cols = st.columns(len(week_days)) if week_days else []
for col, day in zip(cols, week_days):
    with col.container(border=True):
        info = service.content.lesson(day)
        st.caption(f"Day {day}" + (" · 복습" if info.is_review else ""))
        st.markdown(f"**{info.title}**")
        st.caption(ui.STATUS_LABELS[statuses[day]])
        if statuses[day] != "locked" and st.button("열기", key=f"open_day_{day}", width="stretch"):
            ui.go_to_lesson(day)

# ---- 취약 개념 & 복습 추천
left, right = st.columns(2)
with left:
    st.subheader("취약 개념")
    if not stats.weak_concepts:
        st.caption("아직 취약 개념이 없습니다. 문제를 풀수록 정확해집니다.")
    for w in stats.weak_concepts:
        st.markdown(f"**{w.label}** — 제출 {w.submissions}회 중 {w.failed}회 실패 ({ui.percent(w.fail_rate)})"
                    + (f", 미해결 오답 {w.unresolved_notes}개" if w.unresolved_notes else ""))
        st.progress(w.fail_rate)
with right:
    st.subheader("복습 추천")
    if not stats.recommendations:
        st.caption("복습할 항목이 없습니다. 잘하고 있어요!")
    for i, rec in enumerate(stats.recommendations):
        with st.container(border=True):
            if rec.kind == "wrong_note":
                st.markdown(f"**오답 재도전 · Day {rec.day} {rec.title}**")
                st.caption(rec.reason)
                if st.button("다시 풀기", key=f"rec_{i}"):
                    ui.go_to_practice(rec.exercise_id)
            else:
                st.markdown(f"**수업 복습 · Day {rec.day} {rec.title}**")
                st.caption(rec.reason)
                if st.button("수업 열기", key=f"rec_{i}"):
                    ui.go_to_lesson(rec.day, 1)
