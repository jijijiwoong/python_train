@echo off
chcp 65001 >nul
rem Python Learning Lab launcher. Serves on this PC only (localhost) because the app runs Python code.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [오류] .venv 가상환경이 없습니다. README의 설치 방법을 먼저 실행하세요.
    exit /b 1
)
rem Open the browser once the server has had a few seconds to start (ping works even without a console).
start "" /b cmd /c "ping -n 5 127.0.0.1 >nul & start http://localhost:8501"
".venv\Scripts\python.exe" -m streamlit run lab_app\app.py ^
    --server.address localhost --server.port 8501 --server.headless true ^
    --browser.gatherUsageStats false --client.toolbarMode minimal
