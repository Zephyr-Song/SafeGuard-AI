"""CLI compatibility wrapper for SafeBARS deterministic technical evidence."""

from __future__ import annotations

import pathlib
import sys

_REPO = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from modules.technical_evidence import (  # noqa: E402
    CHECK_DEFINITIONS,
    build_public_evidence,
    evaluate_case,
    main,
    run_all,
    seed_cases,
)

__all__ = [
    "CHECK_DEFINITIONS",
    "build_public_evidence",
    "evaluate_case",
    "main",
    "run_all",
    "seed_cases",
]


if __name__ == "__main__":
    raise SystemExit(main())
