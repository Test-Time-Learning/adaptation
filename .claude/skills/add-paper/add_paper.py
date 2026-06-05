#!/usr/bin/env python3
"""Validate and append ONE paper entry to papers.json, then rebuild the site + README.

Usage:
    python add_paper.py entry.json     # entry.json holds one paper object (or a list)
    echo '{...}' | python add_paper.py # or pipe the JSON object on stdin

It validates the entry, rejects duplicates (by normalized title), fills a unique
slug + sensible defaults, LaTeX-escapes non-ASCII in the bibtex, appends to
papers.json, then runs build.py and readme.py.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TASKS = {
    "Classification", "Segmentation", "Detection", "Regression", "Restoration",
    "Retrieval & Ranking", "Sequence & Language", "Decision-Making",
    "Theory", "Benchmark / Survey",
}
DOMAIN = {
    "Image", "Vision-Language", "Video", "3D/Point-Cloud", "Graph", "Speech",
    "Audio", "Text/Document", "Time-Series", "Tabular", "Medical", "Remote-Sensing",
    "Recommendation", "EEG/Bio-signal", "Tactile", "Molecular", "Multimodal",
    "Person-ReID", "Face-Anti-Spoofing",
}
SETTING = {
    "Online", "Continual", "Single-image", "Mixed/Non-i.i.d.", "Federated",
    "Black-box", "Gradient-free", "Open-set", "Label-Shift", "Adversarial",
}
REQUIRED = ("title", "authors", "venue", "url", "task")

# minimal unicode -> LaTeX map for bibtex (display fields keep their unicode)
ESC = {
    "é": "{\\'e}", "è": "{\\`e}", "ê": "{\\^e}", "ë": '{\\"e}', "á": "{\\'a}",
    "à": "{\\`a}", "ä": '{\\"a}', "â": "{\\^a}", "ã": "{\\~a}", "å": "{\\aa}",
    "ö": '{\\"o}', "ó": "{\\'o}", "ò": "{\\`o}", "ô": "{\\^o}", "õ": "{\\~o}",
    "ø": "{\\o}", "ü": '{\\"u}', "ú": "{\\'u}", "ù": "{\\`u}", "û": "{\\^u}",
    "í": "{\\'i}", "ì": "{\\`i}", "î": "{\\^i}", "ï": '{\\"i}', "ñ": "{\\~n}",
    "ç": "{\\c c}", "ß": "{\\ss}", "ł": "{\\l}", "š": "{\\v s}", "ž": "{\\v z}",
    "č": "{\\v c}", "ć": "{\\'c}", "Ö": '{\\"O}', "Ä": '{\\"A}', "Ü": '{\\"U}',
    "É": "{\\'E}", "Ø": "{\\O}", "Ł": "{\\L}",
}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def esc_bib(s):
    return "".join(ESC.get(c, c) for c in (s or ""))


def find_root():
    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        p = base
        for _ in range(8):
            if (p / "papers.json").exists() and (p / "build.py").exists():
                return p
            p = p.parent
    sys.exit("ERROR: could not locate papers.json (run from inside the papers/ repo).")


def slugify(entry, used):
    base = re.sub(r"[^a-z0-9]+", "_",
                  (entry.get("full") or entry.get("title") or "paper").lower()).strip("_")[:40] or "paper"
    s, i = base, 2
    while s in used:
        s = f"{base}_{i}"
        i += 1
    return s


def main():
    root = find_root()
    raw = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else sys.stdin.read()
    data_in = json.loads(raw)
    entries = data_in if isinstance(data_in, list) else [data_in]

    papers = json.loads((root / "papers.json").read_text())
    seen_titles = {norm(p.get("title")) for p in papers}
    used_slugs = {p["slug"] for p in papers}

    added = 0
    for e in entries:
        # validation
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            sys.exit(f"ERROR: missing required field(s): {missing}")
        if e["task"] not in TASKS:
            sys.exit(f"ERROR: task {e['task']!r} not in {sorted(TASKS)}")
        tags = e.get("tags") or []
        unknown = [t for t in tags if t not in DOMAIN and t not in SETTING]
        if unknown:
            sys.exit(f"ERROR: unknown tag(s) {unknown}. Allowed domain={sorted(DOMAIN)} setting={sorted(SETTING)}")
        pres = e.get("presentation") or ""
        if pres not in ("", "Oral", "Spotlight"):
            sys.exit(f"ERROR: presentation must be '', 'Oral', or 'Spotlight' (got {pres!r})")
        if norm(e["title"]) in seen_titles:
            sys.exit(f"ERROR: a paper with this title already exists: {e['title']!r}")
        if not (tags & DOMAIN if isinstance(tags, set) else set(tags) & DOMAIN):
            print(f"WARNING: entry has no domain tag — consider adding one of {sorted(DOMAIN)}")

        slug = e.get("slug") or slugify(e, used_slugs)
        used_slugs.add(slug)
        seen_titles.add(norm(e["title"]))
        rec = {
            "slug": slug,
            "full": e.get("full") or "",
            "title": e["title"],
            "authors": e["authors"],
            "venue": e["venue"],
            "task": e["task"],
            "task_fine": e.get("task_fine") or e["task"],
            "tags": list(tags),
            "url": e["url"],
            "pdf": e.get("pdf") or "",
            "code": e.get("code") or "",
            "bibtex": esc_bib(e.get("bibtex") or ""),
            "presentation": pres,
        }
        papers.append(rec)
        added += 1
        print(f"+ added [{slug}] {rec['full'] or '—'} — {rec['title'][:60]}")

    (root / "papers.json").write_text(json.dumps(papers, indent=2, ensure_ascii=False))
    print(f"papers.json now has {len(papers)} entries (+{added}).")

    # rebuild data.json + README
    for script in ("build.py", "readme.py"):
        if (root / script).exists():
            subprocess.run([sys.executable, str(root / script)], cwd=root, check=True)


if __name__ == "__main__":
    main()
