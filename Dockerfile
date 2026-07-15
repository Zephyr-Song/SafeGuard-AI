# SafeBARS container image — optional, reproducible deployment target.
#
# Render currently deploys via its Python buildpack (see render.yaml,
# `env: python`), which is the active configuration. This Dockerfile exists so
# the exact runtime can be reproduced locally and, if desired, switched on
# Render by setting `env: docker` + `dockerfile: Dockerfile` in render.yaml
# (behaviour is otherwise identical — same gunicorn command, same Python 3.12).
#
# Build:   docker build -t safebars .
# Run:     docker run --rm -p 5000:5000 -e FLASK_SECRET_KEY=dev-only safebars
# Health:  curl http://localhost:5000/healthz

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

WORKDIR /app

# Install dependencies first to maximize layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY . .

EXPOSE 5000

# Mirrors render.yaml startCommand (single worker keeps the Free Tier memory
# footprint small; --timeout 120 covers slow LLM-backed responses).
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120"]
