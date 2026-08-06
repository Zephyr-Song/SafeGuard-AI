from app import app
from flask import jsonify
import os
import datetime


@app.route("/api/version")
def api_version():
    # Render exposes the deployed commit via RENDER_GIT_COMMIT.
    commit = (
        os.environ.get("RENDER_GIT_COMMIT")
        or os.environ.get("GIT_COMMIT")
        or "unknown"
    )
    return jsonify({
        "app": "safebars",
        "commit": commit,
        "python": os.environ.get("PYTHON_VERSION"),
        "deployed_at": datetime.datetime.utcnow().isoformat() + "Z",
    })
