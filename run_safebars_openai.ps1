param(
    [string]$Model = "gpt-4o-mini",
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

Write-Host "Starting SafeBARS with OpenAI LLM mode support..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
    $secureKey = Read-Host "Paste your OpenAI API key. It will only be used for this terminal session" -AsSecureString
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

    $env:OPENAI_API_KEY = $plainKey
}

$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = $Model

Write-Host "OpenAI key detected for this process." -ForegroundColor Green
Write-Host "Model: $env:OPENAI_MODEL" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$Port/safebars" -ForegroundColor Cyan
Write-Host "In the SafeBARS page, check: Use LLM-backed responses." -ForegroundColor Cyan

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=$Port)"
