#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consistency check for the SafeBARS CHI'27 LaTeX bundle (no LaTeX needed)."""
import re, os, glob, sys

PAPER = r"D:\WorkBuddy\SafeGuard-AI-clone\paper"
FIGDIR = os.path.join(PAPER, "figures_export")

draft = open(os.path.join(PAPER, "safebars_chi2027_draft.tex"), encoding="utf-8").read()
pilot = open(os.path.join(PAPER, "safebars_pilot_evaluation.tex"), encoding="utf-8").read()
concept = open(os.path.join(PAPER, "safebars_concept_validation.tex"), encoding="utf-8").read()
# combine draft + all \input'd files so cross-file \ref/\label/\cite resolve
text = "\n".join([draft, pilot, concept])

problems = []

# 1. \input files exist
for m in re.finditer(r"\\input\{([^}]+)\}", draft):
    fn = m.group(1)
    p = os.path.join(PAPER, fn + ".tex")
    if not os.path.exists(p):
        problems.append(f"MISSING \\input file: {fn}.tex")

# 2. figures referenced exist in FIGDIR
for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
    fn = m.group(1)
    cand = os.path.join(FIGDIR, fn)
    if not os.path.exists(cand):
        problems.append(f"MISSING figure file: {fn}")
    else:
        if fn.lower().endswith(".pdf"):
            # check vectorness
            data = open(cand, "rb").read()
            streams = []
            for sm in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
                try: streams.append(__import__("zlib").decompress(sm.group(1)))
                except Exception: pass
            blob = b"\n".join(streams)
            tcount = blob.count(b"Tj") + blob.count(b"TJ")
            dcount = blob.count(b"Do")
            if dcount > 0:
                problems.append(f"RASTER pdf (has image draw): {fn}")
            elif tcount == 0:
                problems.append(f"PDF has no text ops (suspicious): {fn}")

# 3. citations resolve to bibitem
cites = set()
for m in re.finditer(r"\\cite(?:author|year|yearpar)?\{([^}]+)\}", text):
    for k in m.group(1).split(","):
        cites.add(k.strip())
bibkeys = set(re.findall(r"\\bibitem\[[^\]]*]\{([^}]+)\}", draft))
for c in cites:
    if c not in bibkeys:
        problems.append(f"\\cite{{{c}}} has NO \\bibitem")

# 4. \ref have \label
refs = set(re.findall(r"\\ref\{([^}]+)\}", text))
labels = set(re.findall(r"\\label\{([^}]+)\}", text))
for r in refs:
    if r not in labels:
        problems.append(f"\\ref{{{r}}} has NO \\label")

# 5. brace balance (rough) per file
for name, ftext in [("draft", draft), ("pilot", pilot)]:
    depth = 0
    ok = True
    for ch in ftext:
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                ok = False; break
    if depth != 0 or not ok:
        problems.append(f"BRACE imbalance in {name}: depth={depth}")

# 6. CJK leakage in .tex (should be none outside comments)
cjk = re.findall(r"[\u4e00-\u9fff]", text)
# allow CJK only inside % comments? simplest: report count
if cjk:
    problems.append(f"CJK characters found in .tex: {len(cjk)} (should be 0)")

# 7. leftover placeholders (informational)
ph = re.findall(r"\\langle[^\n]*\\rangle", text)
print(f"[info] unfilled \\langle placeholder blocks: {len(ph)} (expected in Study 1 results; real data pending)")

print("\n=== FIGURES referenced ===")
figs = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text)))
for f in figs:
    print("  ", "OK " if os.path.exists(os.path.join(FIGDIR, f)) else "MISS", f)

print("\n=== \input files ===")
for m in re.finditer(r"\\input\{([^}]+)\}", draft):
    print("  ", "OK " if os.path.exists(os.path.join(PAPER, m.group(1)+".tex")) else "MISS", m.group(1))

print("\n=== cites ===", sorted(cites))
print("=== bibkeys ===", sorted(bibkeys))

print("\n=== PROBLEMS ===")
if not problems:
    print("  NONE — bundle is internally consistent.")
else:
    for p in problems:
        print("  -", p)
sys.exit(1 if problems else 0)
