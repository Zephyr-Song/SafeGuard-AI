param(
    [string]$Model = "qwen-plus",
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

Write-Host "Starting SafeBARS with Aliyun Bailian LLM mode support..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:BAILIAN_API_KEY)) {
    $secureKey = Read-Host "Paste your Aliyun Bailian/DashScope API key. It will only be used for this terminal session" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try {
        $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }

    if ([string]::IsNullOrWhiteSpace($plainKey)) {
        Write-Host "No API key provided. Exiting." -ForegroundColor Red
        exit 1
    }

    $env:BAILIAN_API_KEY = $plainKey
}

$env:BAILIAN_MODEL = $Model
$env:BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

Write-Host "Aliyun Bailian key detected for this process." -ForegroundColor Green
Write-Host "Model: $env:BAILIAN_MODEL" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$Port/safebars" -ForegroundColor Cyan
Write-Host "In the SafeBARS page, check: Use LLM-backed responses." -ForegroundColor Cyan

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=$Port)"
