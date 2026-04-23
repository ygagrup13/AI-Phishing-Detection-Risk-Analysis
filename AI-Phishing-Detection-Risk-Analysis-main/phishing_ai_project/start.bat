@echo off
title PhishGuard AI
echo [*] PhishGuard AI baslatiliyor...
cd /d "%~dp0"
if exist "phishing_ai_project" cd phishing_ai_project
start "" cmd /k "py api.py"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000"
echo [+] Tarayici aciliyor...
