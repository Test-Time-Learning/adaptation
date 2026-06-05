---
name: add-paper
description: Add a Test-Time Adaptation paper to this Awesome-TTA reading list (papers.json). Use when the user wants to add, insert, or contribute a TTA/TTT paper to the list — given a title, arXiv/OpenReview/DOI link, or a rough reference. Gathers metadata, classifies the Task and Domain/Setting tags, dedups, appends to papers.json, and rebuilds data.json + README.md.
---

# Add a paper to Awesome Test-Time Adaptation

This repo is a curated reading list of **Test-Time Adaptation (TTA)** / **Test-Time Training (TTT)** papers. `papers.json` is the source of truth; `build.py` produces `data.json` (the website data) and `readme.py` produces `README.md`. Your job for this skill: take a user-supplied paper, build a correct entry, and append it.

## 0. Scope check (do this first)

Only add **genuine test-time adaptation / test-time training** — methods that adapt a trained model **at inference, on unlabeled test data**, to handle distribution shift.

- ✅ Include: TTT (self-supervision at test), entropy-minimization / pseudo-labeling at test (TENT-style), BN-stat adaptation, test-time prompt tuning, online/continual/episodic/single-image TTA, source-free adaptation done *at inference*.
- ❌ Exclude: LLM **test-time scaling / reasoning** with no weight update (best-of-N, CoT); source-free DA that needs a separate **training phase** on the whole target set; domain generalization (train-time only); test-time **augmentation** only (no model/stat update).

If the paper is out of scope, tell the user and stop.

## 1. Gather metadata

From the user's link (arXiv abstract, OpenReview, CVF, DOI) or a web search, collect:

- **title** — exact paper title.
- **authors** — full list, comma-separated, in display form (keep unicode like "Clément"; the script LaTeX-escapes the *bibtex* only).
- **venue** — short form + year, e.g. `NeurIPS 2025`, `CVPR 2024`, `IEEE TPAMI 2025`, `arXiv 2026`. Use standard abbreviations (ICLR, ICML, ECCV, WACV, TMLR, IJCV, ISPRS JPRS, JOS, ESWA…). Do NOT include volume/issue or "(Oral)" here.
- **url** — landing/abstract page (arXiv `/abs/`, OpenReview forum, CVF html, DOI).
- **pdf** — direct PDF link (or "").
- **code** — official repo URL (or "").
- **bibtex** — a valid BibTeX entry. ASCII is preferred; the script will LaTeX-escape any remaining accents automatically.
- **presentation** — `"Oral"`, `"Spotlight"`, or `""` (only for genuine oral/spotlight; never put it in `venue`).
- **full** — the method's short **Name**/acronym (e.g. `TENT`, `CoTTA`, `LN-TTA`). If the paper proposes **no named method**, set it to `""` (the UI shows "—"). Never put the full title here.

## 2. Classify the Task (exactly one)

Pick the single **ML problem** the paper solves:

| Task | What it covers |
|---|---|
| `Classification` | category prediction — image / VLM zero-shot / node / graph / audio / tabular / activity / medical class; also open-set & face-anti-spoofing. |
| `Segmentation` | dense per-pixel / per-point labeling. |
| `Detection` | object / region localization. |
| `Regression` | continuous targets — depth, pose, geometry, time-series forecasting, molecular properties. |
| `Restoration` | recover a clean signal — super-res, denoise, deblur, dehaze, compression, point-cloud upsampling. |
| `Retrieval & Ranking` | match / rank by similarity — cross-modal retrieval, person re-ID, recommendation. |
| `Sequence & Language` | ASR, OCR, language modeling, QA / reasoning, VQA, MT. |
| `Decision-Making` | RL, embodied agents, navigation. |
| `Theory` | primary contribution is theoretical — learnability, provable guarantees, asymptotics. |
| `Benchmark / Survey` | benchmarks, empirical studies, surveys. |

## 3. Assign Tags (Domain + Setting; multi-select)

**Domain** (modality / application — usually 1, sometimes 2). Pick from:
`Image`, `Vision-Language`, `Video`, `3D/Point-Cloud`, `Graph`, `Speech`, `Audio`, `Text/Document`, `Time-Series`, `Tabular`, `Medical`, `Remote-Sensing`, `Recommendation`, `EEG/Bio-signal`, `Tactile`, `Molecular`, `Multimodal`, `Person-ReID`, `Face-Anti-Spoofing`.
Always give at least one domain tag (default `Image` for vision work).

**Setting** (protocol / challenge — typically 0–2; only the *distinctive* ones, the plain corruption / source-free case is the unmarked default):

- `Online` — adapts on a streaming, single-pass, **accumulating** test stream (TENT-style). Don't tag if single-image/episodic or offline.
- `Continual` — the test **domain keeps changing** over a sequence (CTTA / lifelong). (Implies online; usually no need to also add `Online`.)
- `Single-image` — adapts on **one** test image, episodic reset (TPT, MEMO).
- `Mixed/Non-i.i.d.` — temporally-correlated / label-imbalanced / "wild" / non-i.i.d. streams (SAR, NOTE, RoTTA).
- `Federated` — federated / distributed multi-client TTA.
- `Black-box` — only model **outputs**, no weights/gradients.
- `Gradient-free` — backprop-free / training-free / cache-based (T3A, LAME, FOA, VLM caches).
- `Open-set` — novel/unknown classes at test (open-world).
- `Label-Shift` — class-prior shift / imbalance / long-tailed.
- `Adversarial` — adversarial or malicious/poisoned test samples.

Do **not** invent new task or tag values — the helper validates against the fixed vocabulary.

## 4. Append and rebuild

Build the entry as a JSON object and pass it to the helper (it validates, dedups by title, assigns a unique `slug`, LaTeX-escapes the bibtex, appends, and runs `build.py` + `readme.py`):

```bash
cat > /tmp/entry.json <<'JSON'
{
  "full": "TENT",
  "title": "Tent: Fully Test-Time Adaptation by Entropy Minimization",
  "authors": "Dequan Wang, Evan Shelhamer, Shaoteng Liu, Bruno Olshausen, Trevor Darrell",
  "venue": "ICLR 2021",
  "task": "Classification",
  "tags": ["Image", "Online"],
  "url": "https://arxiv.org/abs/2006.10726",
  "pdf": "https://arxiv.org/pdf/2006.10726",
  "code": "https://github.com/DequanWang/tent",
  "bibtex": "@inproceedings{wang2021tent, title={Tent: Fully Test-Time Adaptation by Entropy Minimization}, author={Wang, Dequan and Shelhamer, Evan and Liu, Shaoteng and Olshausen, Bruno and Darrell, Trevor}, booktitle={International Conference on Learning Representations (ICLR)}, year={2021} }",
  "presentation": "Spotlight"
}
JSON
python "$(dirname SKILL.md)/add_paper.py" /tmp/entry.json   # run from the papers/ repo root
```

In practice, run from the repo root: `python .claude/skills/add-paper/add_paper.py /tmp/entry.json`. The script locates `papers.json` automatically and rebuilds. You can also pass a JSON **array** to add several at once.

## 5. Verify

After it runs, confirm: the helper printed `+ added […]` and the new total; `data.json` and `README.md` regenerated without error. If the user is serving the site (`python serve.py`), tell them to refresh.

## Notes
- The entry must be unique by title — the script refuses duplicates. If updating an existing paper, edit `papers.json` directly instead.
- `task_fine` (the original fine-grained label) is optional; if omitted it mirrors `task`.
- Keep `venue` clean (no parentheticals); Oral/Spotlight belongs in `presentation`.
