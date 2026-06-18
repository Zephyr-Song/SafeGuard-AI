param(
    [string]$Model = "glm-4",
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

Write-Host "Starting SafeBARS with Zhipu LLM mode support..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:ZHI_KEY)) {
    $secureKey = Read-Host "Paste your Zhipu API key. It will only be used for this terminal session" -AsSecureString
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

    $env:ZHI_KEY = $plainKey
}

$env:SAFEBARS_LLM_MODEL = $Model

Write-Host "Zhipu key detected for this process." -ForegroundColor Green
Write-Host "Model: $env:SAFEBARS_LLM_MODEL" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$Port/safebars" -ForegroundColor Cyan
Write-Host "In the SafeBARS page, check: Use LLM-backed responses." -ForegroundColor Cyan

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=$Port)"
