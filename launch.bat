@echo off
setlocal
cd /d "%~dp0"
echo Starting ACE-Omega Academic Universe...
python -m streamlit run app.py
pause
