"""Streamlit entry point. Launch with run_app.cmd (binds to localhost only)."""
import sys
from pathlib import Path

# Make `import lab_app` work no matter how Streamlit was launched.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st  # noqa: E402

from lab_app import components as ui  # noqa: E402

LAUNCH_COMMAND = r".venv\Scripts\python -m streamlit run lab_app\app.py --server.address localhost"

st.set_page_config(page_title="Python Learning Lab", page_icon="🐍", layout="wide")

# The app runs user code. Refuse to serve it to other machines on the network.
if st.get_option("server.address") not in ("localhost", "127.0.0.1", "::1"):
    st.error("보안을 위해 이 앱은 이 PC에서만 실행할 수 있습니다. `run_app.cmd`로 실행하거나 "
             "`--server.address localhost` 옵션을 붙여 주세요.")
    st.code(LAUNCH_COMMAND, language="powershell")
    st.stop()

nav = st.navigation({
    "학습": [
        st.Page(ui.PAGE_DASHBOARD, title="대시보드", icon=":material/dashboard:", default=True),
        st.Page(ui.PAGE_LESSON, title="오늘의 수업", icon=":material/school:"),
        st.Page(ui.PAGE_PRACTICE, title="코드 실습", icon=":material/code:"),
    ],
    "기록": [
        st.Page(ui.PAGE_WRONG_NOTES, title="오답 노트", icon=":material/assignment_late:"),
        st.Page(ui.PAGE_HISTORY, title="학습 기록", icon=":material/history:"),
    ],
}, expanded=True)

service = ui.get_service()
with st.sidebar:
    stats = service.dashboard_stats()
    st.divider()
    st.caption("🐍 Python Learning Lab")
    st.caption(f"🔥 연속 {stats.streak}일 · 완료 {stats.completed_days}/{stats.total_days}일")
    st.progress(stats.curriculum_progress)

nav.run()
