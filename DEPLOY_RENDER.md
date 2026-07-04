# Deploy SafeBARS to Render

The repository includes a Render Blueprint in `render.yaml`.

## Blueprint deployment

1. Push the repository to GitHub.
2. In Render, choose **New + -> Blueprint**.
3. Connect `Zephyr-Song/SafeGuard-AI`.
4. Let Render read `render.yaml`.
5. Generate and set a long random `FLASK_SECRET_KEY`.
6. Add only the LLM-provider keys required for the demonstration.
7. Deploy and verify `/healthz`, then `/safebars`.

The main routes are:

- `https://YOUR-SERVICE.onrender.com/safebars`
- `https://YOUR-SERVICE.onrender.com/safebars/expert`
- `https://YOUR-SERVICE.onrender.com/healthz`

## Access controls

`SAFEBARS_REQUIRE_ROLE_AUTH=1` is enabled in the Blueprint. A newly created v2 session receives separate researcher and expert capability tokens; raw tokens are not stored in SQLite.

For a password-protected demonstration, also set:

```dotenv
ENABLE_DEMO_AUTH=1
SAFEBARS_DEMO_USER=safebars
SAFEBARS_DEMO_PASSWORD=replace_with_a_long_random_password
```

Keep `ENABLE_DEMO_AUTH=0` if invited users need to access the public researcher and expert flows without a shared outer password.

## Storage limitation

The free Render plan uses ephemeral local storage. The Blueprint therefore writes the prototype SQLite database to `/tmp/safebars_v2.db`. Sessions, review history, and invitation tokens may disappear on restart, sleep recovery, or redeploy.

Do not use the free-plan configuration for real ethics applications or confidential research materials. Production use requires:

- a persistent managed database;
- institution-managed accounts and case assignment;
- encryption, retention, deletion, backup, and incident procedures;
- security and privacy review;
- validation by the relevant ethics and governance experts.

## Manual service settings

- Runtime: Python
- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- Health check: `/healthz`
