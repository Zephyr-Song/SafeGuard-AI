@echo off
setlocal
cd /d "%~dp0"

echo Starting SafeBARS three-provider comparison on http://127.0.0.1:5054/safebars
echo.
echo This window can configure Zhipu, Aliyun Bailian, and Tencent TokenHub together.
echo Keys are only used in this terminal window.
echo.

set /p ZHI_KEY=Zhipu API key (press Enter to use .env or skip): 
if not "%ZHI_KEY%"=="" (
  set ZHI_MODEL=glm-4
)

set /p BAILIAN_API_KEY=Aliyun Bailian/DashScope API key (press Enter to skip): 
if not "%BAILIAN_API_KEY%"=="" (
  set BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  set BAILIAN_MODEL=qwen-plus
)

set /p TENCENT_API_KEY=Tencent TokenHub API key (press Enter to skip): 
if not "%TENCENT_API_KEY%"=="" (
  set TENCENT_BASE_URL=https://tokenhub.tencentmaas.com/v1
  set TENCENT_MODEL=hy3-preview
  set TENCENT_LABEL=Tencent TokenHub HY3 Preview
)

echo.
echo Open http://127.0.0.1:5054/safebars
echo Use Start Session, type one question, then click Compare Providers.
echo Keep this window open while using the page.
echo.

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=5054)"

pause
