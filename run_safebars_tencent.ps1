param(
    [string]$Model = "hy3-preview",
    [string]$BaseUrl = "https://tokenhub.tencentmaas.com/v1",
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

Write-Host "Starting SafeBARS with Tencent TokenHub LLM mode support..." -ForegroundColor Cyan
Write-Host "This expects a Tencent TokenHub Bearer API key." -ForegroundColor Yellow

if ([string]::IsNullOrWhiteSpace($env:TENCENT_API_KEY)) {
    $secureKey = Read-Host "Paste your Tencent Hunyuan API key. It will only be used for this terminal session" -AsSecureString
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

    $env:TENCENT_API_KEY = $plainKey
}

$env:TENCENT_BASE_URL = $BaseUrl
$env:TENCENT_MODEL = $Model
$env:TENCENT_LABEL = "Tencent TokenHub HY3 Preview"

Write-Host "Tencent key detected for this process." -ForegroundColor Green
Write-Host "Model: $env:TENCENT_MODEL" -ForegroundColor Green
Write-Host "Base URL: $env:TENCENT_BASE_URL" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$Port/safebars" -ForegroundColor Cyan
Write-Host "In the SafeBARS page, check: Use LLM-backed responses." -ForegroundColor Cyan

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=$Port)"
