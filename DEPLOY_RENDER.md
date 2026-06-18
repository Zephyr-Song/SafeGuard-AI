# Deploy SafeBARS to Render

This project is now prepared for Render deployment.

## What was added

- `wsgi.py`: production WSGI entry point.
- `render.yaml`: Render Blueprint config.
- `.renderignore`: keeps local env files and generated data out of deployment.
- `gunicorn` in `requirements.txt`.
- Optional HTTP Basic Auth through `SAFEBARS_DEMO_PASSWORD`.

## Important

Do not upload `.env` or `.env.local`. They contain local API keys and are ignored.

## Option A: Render Blueprint

1. Push this folder to a GitHub repository.
2. Go to Render and choose **New +** -> **Blueprint**.
3. Connect the GitHub repository.
4. Render will read `render.yaml`.
5. In Render environment variables, fill these secret values:
   - `FLASK_SECRET_KEY`
   - `SAFEBARS_DEMO_PASSWORD`
   - `ZHI_KEY`
   - `BAILIAN_API_KEY`
   - `TENCENT_API_KEY`
6. Deploy.
7. Open:
   - `https://YOUR-RENDER-URL/safebars`
   - `https://YOUR-RENDER-URL/healthz`

## Option B: Manual Web Service

Use these settings:

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

Set the same environment variables listed above.

## Demo password

If `SAFEBARS_DEMO_PASSWORD` is set, the website will ask for a browser username and password.

- Username: `safebars`
- Password: the value you set in Render

If `SAFEBARS_DEMO_PASSWORD` is empty, the site is public.
