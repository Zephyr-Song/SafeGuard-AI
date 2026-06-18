param(
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

function Read-SecretToEnv {
    param(
        [string]$Prompt,
        [string]$EnvName
    )
    $secureValue = Read-Host $Prompt -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try {
        $plainValue = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if (-not [string]::IsNullOrWhiteSpace($plainValue)) {
        Set-Item -Path "Env:$EnvName" -Value $plainValue
        return $true
    }
    return $false
}

Write-Host "SafeBARS provider comparison startup" -ForegroundColor Cyan
Write-Host "Keys are only set for this terminal process. They are not written to files." -ForegroundColor Cyan

$useZhipu = Read-Host "Configure Zhipu? (y/n)"
if ($useZhipu -match "^[Yy]") {
    Read-SecretToEnv -Prompt "Paste Zhipu API key" -EnvName "ZHI_KEY" | Out-Null
    $zhipuModel = Read-Host "Zhipu model [glm-4]"
    if ([string]::IsNullOrWhiteSpace($zhipuModel)) { $zhipuModel = "glm-4" }
    $env:ZHI_MODEL = $zhipuModel
}

$useBailian = Read-Host "Configure Aliyun Bailian/DashScope? (y/n)"
if ($useBailian -match "^[Yy]") {
    Read-SecretToEnv -Prompt "Paste Aliyun Bailian/DashScope API key" -EnvName "BAILIAN_API_KEY" | Out-Null
    $bailianModel = Read-Host "Bailian model [qwen-plus]"
    if ([string]::IsNullOrWhiteSpace($bailianModel)) { $bailianModel = "qwen-plus" }
    $env:BAILIAN_MODEL = $bailianModel
    $env:BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
}

$useTencent = Read-Host "Configure Tencent TokenHub? (y/n)"
if ($useTencent -match "^[Yy]") {
    Read-SecretToEnv -Prompt "Paste Tencent TokenHub API key" -EnvName "TENCENT_API_KEY" | Out-Null
    $tencentModel = Read-Host "Tencent model [hy3-preview]"
    if ([string]::IsNullOrWhiteSpace($tencentModel)) { $tencentModel = "hy3-preview" }
    $tencentBaseUrl = Read-Host "Tencent TokenHub base URL [https://tokenhub.tencentmaas.com/v1]"
    if ([string]::IsNullOrWhiteSpace($tencentBaseUrl)) { $tencentBaseUrl = "https://tokenhub.tencentmaas.com/v1" }
    $env:TENCENT_MODEL = $tencentModel
    $env:TENCENT_BASE_URL = $tencentBaseUrl
    $env:TENCENT_LABEL = "Tencent TokenHub HY3 Preview"
}

$useProfileA = Read-Host "Configure comparison provider A? (y/n)"
if ($useProfileA -match "^[Yy]") {
    $labelA = Read-Host "Provider A label [Provider A]"
    if ([string]::IsNullOrWhiteSpace($labelA)) { $labelA = "Provider A" }
    $env:LLM_A_LABEL = $labelA
    $env:LLM_A_BASE_URL = Read-Host "Provider A base URL, e.g. https://api.openai.com/v1"
    $modelA = Read-Host "Provider A model"
    $env:LLM_A_MODEL = $modelA
    Read-SecretToEnv -Prompt "Provider A API key" -EnvName "LLM_A_API_KEY" | Out-Null
}

$useProfileB = Read-Host "Configure comparison provider B? (y/n)"
if ($useProfileB -match "^[Yy]") {
    $labelB = Read-Host "Provider B label [Provider B]"
    if ([string]::IsNullOrWhiteSpace($labelB)) { $labelB = "Provider B" }
    $env:LLM_B_LABEL = $labelB
    $env:LLM_B_BASE_URL = Read-Host "Provider B base URL, e.g. https://open.bigmodel.cn/api/paas/v4"
    $modelB = Read-Host "Provider B model"
    $env:LLM_B_MODEL = $modelB
    Read-SecretToEnv -Prompt "Provider B API key" -EnvName "LLM_B_API_KEY" | Out-Null
}

Write-Host "Open: http://127.0.0.1:$Port/safebars" -ForegroundColor Green
Write-Host "Use Start Session, type a question, then click Compare Providers." -ForegroundColor Green

python -c "from app import app; app.run(debug=False, host='127.0.0.1', port=$Port)"
