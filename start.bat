@echo off
chcp 65001 >nul
echo ========================================
echo SafeGuard AI - 启动中...
echo ========================================
echo.
echo 正在加载配置...
echo 智谱AI API密钥: 已配置
echo 模型: GLM-4
echo.
echo 启动Web服务器...
echo 访问地址: http://localhost:5000
echo.
python app.py
pause
