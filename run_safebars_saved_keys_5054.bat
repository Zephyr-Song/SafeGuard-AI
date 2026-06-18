@echo off
setlocal
cd /d "%~dp0"

echo Starting SafeBARS using saved keys from .env.local
echo Open http://127.0.0.1:5054/safebars
echo Keep this window open while using the page.
echo.
echo If providers do not appear, edit .env.local and restart this file.
echo.

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=5054)"

pause
