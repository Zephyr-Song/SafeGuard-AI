# SafeBARS LLM Setup Note

Last updated: 2026-06-17

## What This Does

SafeBARS runs in deterministic template mode by default.

If a Zhipu, Aliyun Bailian, Tencent Hunyuan, or explicitly enabled OpenAI-compatible API key is configured and the UI checkbox is enabled, SafeBARS can call an LLM for more natural stakeholder responses.

## Safe Startup Method

### Zhipu

Use:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_zhipu.ps1
```

The script will ask for your Zhipu API key.

The key is only set for that terminal session and the Flask process started from it. It is not written into code.

### Aliyun Bailian / DashScope

Use:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_bailian.ps1
```

Default endpoint:

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

Default model:

```text
qwen-plus
```

You can override:

```powershell
.\run_safebars_bailian.ps1 -Model "qwen-plus"
```

### OpenAI

Use:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_openai.ps1
```

Default endpoint:

```text
https://api.openai.com/v1
```

Default model:

```text
gpt-4o-mini
```

You can override:

```powershell
.\run_safebars_openai.ps1 -Model "gpt-4o-mini"
```

OpenAI is now disabled by default in the generic provider loader. It only appears when `ENABLE_OPENAI_PROVIDER=1` is set, or when using the OpenAI-specific startup script.

### Tencent Hunyuan

Use:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_tencent.ps1
```

Default endpoint:

```text
https://api.hunyuan.cloud.tencent.com/v1
```

Default model:

```text
hunyuan-turbo
```

If your Tencent credential is a SecretId/SecretKey pair instead of an OpenAI-compatible API key, this adapter will not work yet. It would require Tencent Cloud SDK request signing.

## Then In Browser

Open:

```text
http://127.0.0.1:5050/safebars
```

Then:

1. Check `Use LLM-backed responses`.
2. Click `Start Session`.
3. Send a rehearsal question.

If the LLM call fails or times out, SafeBARS should fall back to deterministic template responses.

## Compare Different Providers/API Keys

Use:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_compare.ps1 -Port 5051
```

The script can configure:

- Zhipu through `ZHI_KEY`;
- Aliyun Bailian through `BAILIAN_API_KEY`;
- Tencent Hunyuan through `TENCENT_API_KEY`;
- OpenAI through `OPENAI_API_KEY` only when explicitly enabled;
- Provider A through `LLM_A_API_KEY`, `LLM_A_BASE_URL`, `LLM_A_MODEL`;
- Provider B through `LLM_B_API_KEY`, `LLM_B_BASE_URL`, `LLM_B_MODEL`.

Then open:

```text
http://127.0.0.1:5051/safebars
```

Workflow:

1. Click `Start Session`.
2. Type one rehearsal question.
3. Click `Compare Providers`.

The page will show:

- template fallback response;
- each configured provider response;
- provider label;
- model;
- masked key hint.

The full API key is never displayed in the page.

## Optional Model Override

Default model:

```text
glm-4
```

You can override:

```powershell
.\run_safebars_zhipu.ps1 -Model "glm-4"
```

## Do Not Commit API Keys

Do not paste API keys into:

- source code;
- research notes;
- screenshots;
- exported study data;
- Git commits.

The project now includes `.gitignore` entries for `.env` and study export folders.

## How The Code Detects Zhipu

SafeBARS checks:

```text
ZHI_KEY
```

When `ZHI_KEY` exists, the LLM client uses:

```text
https://open.bigmodel.cn/api/paas/v4
```

When `BAILIAN_API_KEY`, `DASHSCOPE_API_KEY`, or `ALIYUN_API_KEY` exists, the LLM client uses:

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

The model is read from:

```text
SAFEBARS_LLM_MODEL
```

Provider-specific model variables:

```text
ZHI_MODEL
BAILIAN_MODEL
OPENAI_MODEL
```
