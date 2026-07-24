"""Compatibility wrapper for the production technical-evidence seed corpus."""

import pathlib
import sys

_REPO = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from modules.technical_evidence_cases import (
    SEED_CASES,
    case_to_project,
    get_seed_cases,
)

__all__ = ["SEED_CASES", "case_to_project", "get_seed_cases"]
