# SafeBARS Local API Key Setup

Last updated: 2026-06-18

## Recommended Method

Use `.env.local` for local API keys.

Steps:

1. Copy `.env.local.example`.
2. Rename the copy to `.env.local`.
3. Open `.env.local` in Notepad.
4. Paste your keys after the `=` signs.
5. Save the file.
6. Start SafeBARS with saved keys.

## Example

```text
ZHI_KEY=your_zhipu_key_here
BAILIAN_API_KEY=your_bailian_key_here
TENCENT_API_KEY=your_tencent_hunyuan_key_here
```

Do not add quotation marks unless the key itself contains quotation marks.

## Start With Saved Keys

Run:

```powershell
cd C:\Users\song\Desktop\SafeGuard-AI
.\run_safebars_saved_keys_5054.bat
```

Then open:

```text
http://127.0.0.1:5054/safebars
```

## Compare Providers

Use:

```text
Start Session -> type a prompt -> Compare Providers
```

The provider list should include the services you configured in `.env.local`.

OpenAI/GPT is intentionally excluded from the local config.

## Safety Note

`.env.local` is ignored by git. Do not share it, screenshot it, or paste it into chat.
