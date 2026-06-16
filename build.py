#!/usr/bin/env python3
"""Build data.json for the Awesome-TTA Paper List static site.

Reads papers.json, derives the venue badge fields, and writes a compact
data.json consumed by index.html.

    python build.py

To add a paper: append one object to papers.json (keep one object per line) with
keys slug, full, title, authors, venue, task, url, pdf, code, bibtex, presentation,
then re-run this script.
"""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_JOURNAL = ("tmlr", "ijcv", "jmlr", "tpami", "pami", "pattern recognition", "journal of",
            "transactions", "tmi", "media", "tip", "tnnls", "imwut", "scientific reports",
            "expert systems", "isprs", "photogrammetry", "remote sensing",
            "eswa", "jprs", "sci. rep", "j. softw", "jos", "jag", "tcsvt", "tmm", "tcss",
            "nature communications", "nature commun")
_CONF = ("iclr", "neurips", "icml", "cvpr", "iccv", "eccv", "aaai", "wacv", "aistats",
         "bmvc", "ijcai", "acl", "emnlp", "naacl", "kdd", "3dv", "icra", "miccai", "iros",
         "interspeech", "asru", "icassp", "wsdm", "www", "mm", "bci", "icdar",
         "recsys", "collas", "uai", "ijcnn")


def parse_year(venue: str):
    m = re.search(r"\b(19|20)\d{2}\b", venue or "")
    return int(m.group(0)) if m else None


def classify_venue(venue: str):
    """Return (display_label, venue_name, venue_type ∈ conference|journal|other)."""
    v = venue or ""
    low = v.lower()
    label = re.sub(r"\s*\((oral|spotlight|notable[^)]*)\)", "", v, flags=re.I).strip()
    label = re.sub(r"\bCommunications\b", "Comm.", label)
    name = re.sub(r"\b\d{4}\b.*$", "", label).replace("Workshop", "").strip(" ,")
    if "workshop" in low or "arxiv" in low or "preprint" in low:
        vtype = "other"
    elif any(t in low for t in _JOURNAL):
        vtype = "journal"
    elif any(re.search(r"\b" + t + r"\b", low) for t in _CONF):
        vtype = "conference"
    else:
        vtype = "other"
    return label, name, vtype


def main():
    papers = json.loads((ROOT / "papers.json").read_text())
    out_papers = []
    for p in papers:
        label, vname, vtype = classify_venue(p.get("venue") or "")
        out_papers.append({
            "slug": p.get("slug"), "full": p.get("full") or "",
            "title": p.get("title"), "authors": p.get("authors"),
            "venue": p.get("venue"), "venue_label": label, "venue_name": vname, "venue_type": vtype,
            "year": parse_year(p.get("venue")),
            "presentation": p.get("presentation"), "task": p.get("task") or "Classification",
            "tags": p.get("tags") or [],
            "url": p.get("url"), "pdf": p.get("pdf"), "code": p.get("code"), "bibtex": p.get("bibtex"),
        })
    out_papers.sort(key=lambda x: (x["full"] or "").lower())
    site = json.loads((ROOT / "meta.json").read_text()) if (ROOT / "meta.json").exists() else {}
    meta = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "n_papers": len(out_papers)}
    meta.update(site)  # name / motto / definition
    out = {"meta": meta, "papers": out_papers}
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"Wrote {len(out_papers)} papers -> docs/data.json")


if __name__ == "__main__":
    main()
