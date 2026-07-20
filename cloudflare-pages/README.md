# SafeBARS Cloudflare Pages entry point

This directory deploys a Cloudflare Pages Function that exposes the existing
SafeBARS application through a `pages.dev` domain. The proxy preserves all
researcher pages, expert invitation fragments, API requests, role headers, and
document downloads while the Python application remains on Render.

## Local check

From this directory:

```powershell
npx wrangler pages dev public
```

Then open `http://127.0.0.1:8788/safebars`.

## Deploy

```powershell
npx wrangler pages deploy public --project-name safebars-ai
```

The upstream is fixed in `functions/[[path]].js` so this cannot be used as an
open proxy. API keys remain on the Render server and are never placed in Pages
or browser code.
