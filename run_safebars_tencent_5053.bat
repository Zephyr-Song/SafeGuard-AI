@echo off
setlocal
cd /d "%~dp0"

echo Starting SafeBARS Tencent TokenHub mode on http://127.0.0.1:5053/safebars
echo.
echo This expects a Tencent TokenHub Bearer API key.
echo.

set /p TENCENT_API_KEY=Tencent TokenHub API key: 
if "%TENCENT_API_KEY%"=="" (
  echo No API key provided.
  pause
  exit /b 1
)

set TENCENT_BASE_URL=https://tokenhub.tencentmaas.com/v1
set TENCENT_MODEL=hy3-preview
set TENCENT_LABEL=Tencent TokenHub HY3 Preview

echo.
echo Tencent TokenHub key detected for this window.
echo Model: %TENCENT_MODEL%
echo Base URL: %TENCENT_BASE_URL%
echo Open http://127.0.0.1:5053/safebars
echo Keep this window open while using the page.
echo.

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=5053)"

pause
