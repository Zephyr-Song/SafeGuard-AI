#!/usr/bin/env powershell
# SafeGuard AI - Flask 版本一键启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SafeGuard AI - Flask 版本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# 检查 Python
Write-Host "检查 Python..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 错误：未找到 Python" -ForegroundColor Red
    Write-Host "请先安装 Python 3.8+" -ForegroundColor Red
    Read-Host "按 Enter 退出"
    exit 1
}
Write-Host "✅ Python 已安装: $pythonCheck" -ForegroundColor Green

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -q flask requests python-dotenv openai 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 服务器启动成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 访问地址：" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   - 按 Ctrl+C 停止服务器" -ForegroundColor White
Write-Host "   - 在浏览器中打开上面的地址" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 启动 Flask 应用
python app.py

Read-Host "按 Enter 退出"
