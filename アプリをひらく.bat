@echo off
chcp 65001 > nul
cd /d "%~dp0"

set "APP_PYTHON=C:\Users\h_79_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%APP_PYTHON%" (
  echo Python が みつかりません。
  echo この がめんを とじずに、Codexへ おしえてください。
  pause
  exit /b 1
)

echo ひらがなアプリを ひらいています...
"%APP_PYTHON%" -m streamlit run app.py

pause
