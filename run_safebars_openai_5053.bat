@echo off
setlocal
cd /d "%~dp0"

echo Starting SafeBARS OpenAI mode on http://127.0.0.1:5053/safebars
echo.
echo Paste your OpenAI API key below. It will only be used in this terminal window.
set /p OPENAI_API_KEY=OpenAI API key: 

if "%OPENAI_API_KEY%"=="" (
  echo No API key provided.
  pause
  exit /b 1
)

set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini

echo.
echo OpenAI key detected for this window.
echo Model: %OPENAI_MODEL%
echo Open http://127.0.0.1:5053/safebars
echo Keep this window open while using the page.
echo.

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=5053)"

pause
