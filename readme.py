#!/usr/bin/env python3
"""Generate README.md for the Awesome Test-Time Adaptation repo from papers.json.

Run after editing papers.json (or after build.py):
    python readme.py
It reads papers.json (source of truth) and docs/data.json (for venue_label / year /
venue_type, produced by build.py) and writes README.md.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = "https://github.com/Test-Time-Learning/adaptation"
SITE = "https://test-time.cc/adaptation/"
MAINTAINER = ("Zhi Zhou", "https://zhouz.dev")

# Task display order: ML problems first, then the two meta buckets last.
TASK_ORDER = [
    "Benchmark / Survey", "Theory",
    "Classification", "Segmentation", "Detection", "Regression", "Restoration",
    "Retrieval & Ranking", "Sequence & Language", "Decision-Making",
]
SETTING = {"Online", "Continual", "Single-image", "Mixed/Non-i.i.d.", "Federated",
           "Black-box", "Gradient-free", "Open-set", "Label-Shift", "Adversarial"}


def slugify_anchor(s: str) -> str:
    """GitHub-style heading anchor."""
    a = s.lower()
    a = a.replace("&", "").replace("/", "").replace(".", "")
    a = re.sub(r"[^a-z0-9 -]", "", a)
    return re.sub(r"\s+", "-", a.strip())


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    papers = json.loads((ROOT / "papers.json").read_text())
    built = json.loads((ROOT / "docs" / "data.json").read_text())
    meta = built.get("meta", {})
    by_slug = {p["slug"]: p for p in built.get("papers", [])}

    date = (meta.get("generated_at") or "")[:10]
    n = len(papers)
    site = json.loads((ROOT / "meta.json").read_text()) if (ROOT / "meta.json").exists() else {}
    name = site.get("name", "Awesome Test-Time Adaptation")
    motto = site.get("motto", "")
    definition = site.get("definition", "")
    # bold the leading "Test-Time Adaptation (TTA)" in the definition for the README
    def_md = definition.replace("Test-Time Adaptation (TTA)", "**Test-Time Adaptation (TTA)**", 1)

    # group by task
    groups: dict[str, list] = {}
    for p in papers:
        groups.setdefault(p.get("task") or "Classification", []).append(p)
    # any task not in TASK_ORDER goes at the end (alphabetical)
    ordered_tasks = [t for t in TASK_ORDER if t in groups] + \
        sorted(t for t in groups if t not in TASK_ORDER)

    out: list[str] = []
    out.append(f"# {name} [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)")
    out.append("")
    if motto:
        out.append(f"> *{motto}*")
        out.append(">")
    if def_md:
        out.append(f"> {def_md}")
    out.append("")
    date_badge = date.replace("-", "--")  # shields.io treats single '-' as a field separator
    out.append('<p align="center">')
    out.append(f'  <img src="https://img.shields.io/badge/Papers-{n}-13b3a8" alt="Papers">')
    out.append(f'  <img src="https://img.shields.io/badge/Last%20Update-{date_badge}-c2902f" alt="Last Update">')
    out.append('</p>')
    out.append("")
    out.append(f"A curated, task-organized reading list of **{n}** Test-Time Adaptation (Training) "
               "papers. Each entry is filed under one **Task** (the ML problem) "
               "and tagged with its **Domain** and **Setting**. "
               f"An interactive, filterable version of this list is available on the "
               f"[project website]({SITE}).")
    out.append("")
    out.append(f"Maintained by [{MAINTAINER[0]}]({MAINTAINER[1]}). "
               "Contributions are welcome; see [Contributing](#contributing).")
    out.append("")

    # taxonomy note
    out.append("## Taxonomy")
    out.append("")
    out.append("- **Task** is the fundamental ML problem: "
               + ", ".join(f"`{t}`" for t in TASK_ORDER) + ".")
    out.append("")

    # table of contents
    out.append("## Contents")
    out.append("")
    for t in ordered_tasks:
        out.append(f"- [{t}](#{slugify_anchor(t)}) ({len(groups[t])})")
    out.append("")

    # one section per task
    for t in ordered_tasks:
        rows = groups[t]

        def sort_key(p):
            y = (by_slug.get(p["slug"], {}) or {}).get("year") or 0
            return (-int(y), (p.get("full") or p.get("title") or "").lower())
        rows = sorted(rows, key=sort_key)

        out.append(f"## {t}")
        out.append("")
        out.append("| Name | Paper | Venue | Links |")
        out.append("|---|---|---|---|")
        for p in rows:
            b = by_slug.get(p["slug"], {})
            name = esc(p.get("full") or "")
            name_cell = f"**{name}**" if name else ""
            title = esc(p.get("title") or "")
            url = p.get("url") or ""
            paper = f"[{title}]({url})" if url else title
            venue = esc(b.get("venue_label") or p.get("venue") or "")
            pres = p.get("presentation")
            if pres:
                venue += f" ({pres})"
            links = []
            if p.get("pdf"):
                links.append(f"[PDF]({p['pdf']})")
            if p.get("code"):
                links.append(f"[Code]({p['code']})")
            links_s = " · ".join(links)
            out.append(f"| {name_cell} | {paper} | {venue} | {links_s} |")
        out.append("")

    out.append("## Contributing")
    out.append("")
    out.append("Spotted a missing paper or an error? Pull requests are welcome. "
               "There are two ways to add a paper.")
    out.append("")
    out.append("### Option A: with Claude Code (recommended)")
    out.append("")
    out.append(f"The repo ships an [`add-paper` skill]({REPO}/tree/main/.claude/skills/add-paper) "
               "for Claude Code. Open the repo in Claude Code and just say, for example, "
               "*\"add this paper: an arXiv link, a conference page, or simply the paper's title\"*. "
               "Given only a title, the skill searches for the paper itself. It then reads the abstract, "
               "decides the Task and the Domain/Setting tags, writes the BibTeX, checks for duplicates, "
               "appends the entry to `papers.json`, and regenerates `data.json` and `README.md`. "
               "You just review the diff and open a PR.")
    out.append("")
    out.append("### Option B: by hand")
    out.append("")
    out.append("1. Append one object to `papers.json` with the fields "
               "`full, title, authors, venue, task, tags, url, pdf, code, bibtex, presentation`.")
    out.append("2. Optionally run `python build.py` and `python readme.py` to preview locally.")
    out.append("3. Open a pull request that commits **only `papers.json`**. "
               "`data.json` and `README.md` are auto-generated and will be regenerated by the maintainer.")
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"<sub>This README is auto-generated by `readme.py` from `papers.json`. "
               f"Last update: {date}. Page designed by [{MAINTAINER[0]}]({MAINTAINER[1]}).</sub>")
    out.append("")

    (ROOT / "README.md").write_text("\n".join(out))
    print(f"Wrote README.md: {n} papers across {len(ordered_tasks)} tasks.")


if __name__ == "__main__":
    main()
