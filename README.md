# OpenSCI-Ocean

**10 parallel experiments: Can AI drive Nature-level papers in ocean science?**

10 个研究方向并行推进。AI 从选题到投稿全流程主导，人类负责物理把关和审核纠偏。全过程公开。

---

## What This Is

10 independent research projects, each exploring a different scientific question in physical oceanography and ocean remote sensing. AI (Claude, GPT, etc.) serves as the primary research engine — literature review, data analysis, figure generation, manuscript writing. Human scientists provide physical intuition, error checking, and quality control.

Each project runs on a fast cycle:

```
Day 0         Day 1            Day 2-3           Day 4-7          Day 7+
Topic lock → AI first draft → Human review → Internal review → Submit
```

Failures, dead ends, and rejections are part of the experiment and will be visible.

## Projects

See [projects/DASHBOARD.md](projects/DASHBOARD.md) for live status of all 10 projects.

| # | Direction | Status |
|---|---|---|
| [P01](projects/p01/) | Submesoscale air-sea coupling regime transition (SWOT) | 🔬 D0 |
| [P02](projects/p02/) | Topological equatorial wave robustness & breakdown (SWOT) | ✍️ D1 |
| [P03](projects/p03/) | Neglected eddy boundary signals (SWOT altimetry) | 🔬 D0 |
| [P04](projects/p04/) | Antarctic sea ice tipping point — SWOT SSH/EKE evidence | ✍️ D1 |
| [P05](projects/p05/) | Deep ocean mixing energy deficit — SWOT SSH constraints | ✍️ D1 |
| [P06](projects/p06/) | TBD | ⬜ |
| [P07](projects/p07/) | TBD | ⬜ |
| [P08](projects/p08/) | TBD | ⬜ |
| [P09](projects/p09/) | TBD | ⬜ |
| [P10](projects/p10/) | TBD | ⬜ |

Each project is self-contained in its own directory with literature, analysis scripts, figures, manuscript, and AI interaction logs.

## Research Scope

**Target journals:** Nature Geoscience, Nature Climate Change, Nature Communications, and other high-impact journals.

**Directions include (not limited to):**
- Satellite ocean dynamic remote sensing (altimetry, SWOT, SAR)
- Physical oceanography (mesoscale eddies, submesoscale dynamics, internal waves)
- Air-sea interaction
- Polar ocean and cryosphere

## Tools & Data

**AI:** Claude, GPT, and other LLMs as the core production tool

**Software:** Python, MATLAB, GMT

**Public data:** SWOT L3/L4, CMEMS, ERA5, Argo, AVISO, WOD, etc.

**In-situ observations:** GNSS wave-tide integrated buoys developed by Qingdao Anhai, with continuous field measurements across multiple sea areas. Some data remain unpublished — suitable for satellite validation or independent research.

## How to Participate

Each project operates independently. You can join one or more projects based on your expertise and interest. Authorship is per-project, based on actual contributions tracked via GitHub.

**Ways to contribute:**
- **Ideas & hypotheses** — A question worth asking but no time to pursue? AI can run the exploration.
- **Physical-intuition review** — Judge whether AI's analysis makes physical sense.
- **Error checking** — Catch hallucinated references, wrong magnitudes, skipped derivations.
- **Literature tracking** — Confirm novelty, find benchmark papers.

**To join:** Open an Issue, submit a PR, or contact via WeChat group (see [recruitment post](docs/recruitment_cn.md)).

## Repository Structure

```
OpenSCI-Ocean/
├── README.md                 # This file
├── COLLABORATION.md          # Rules, authorship, workflow
├── CONTRIBUTORS.md           # Contribution tracking
├── LICENSE                   # MIT
├── projects/
│   ├── DASHBOARD.md          # Status overview of all 10 projects
│   ├── PROJECT_TEMPLATE.md   # Template for new projects
│   ├── p01/                  # Project 01 (independent, self-contained)
│   │   ├── README.md         # Project card: question, status, data links
│   │   ├── literature/       # AI literature review notes
│   │   ├── analysis/         # Scripts + data source links (no raw data)
│   │   ├── figures/          # All generated figures (incl. intermediate)
│   │   ├── manuscript/
│   │   │   ├── v1_ai_draft/  # AI-generated first draft
│   │   │   ├── v2_delivery/  # Human-reviewed delivery draft
│   │   │   ├── v3_final/     # Internally reviewed final draft
│   │   │   └── submitted/    # Submitted version + cover letter
│   │   └── logs/             # AI prompt logs
│   ├── p02/ ... p10/         # Projects 02-10 (same structure)
├── shared/                   # Shared utilities
└── docs/                     # General documentation
```

**No raw data in this repo.** GitHub stores only data source links, download scripts, analysis code, figures, and the complete manuscript evolution from AI draft to final submission.

## Key Questions

1. What percentage of a high-quality paper can AI complete independently?
2. Where does it fail most in mechanism-driven disciplines?
3. What is the irreplaceable human contribution?
4. How fast can this human-AI loop produce publishable science?

## Rules & Documentation

| Document | Purpose |
|---|---|
| [COLLABORATION.md](COLLABORATION.md) | Authorship, roles, workflow, IP, data policy |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to fork, branch, commit, PR |
| [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md) | D2/D3 stage review checklists |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Behavioral expectations |
| [CONTRIBUTORS.md](CONTRIBUTORS.md) | Contribution tracking board |
| [shared/ai_workflow.md](shared/ai_workflow.md) | AI prompt templates for each stage |
| [shared/data_sources.md](shared/data_sources.md) | Public data source directory |
| [shared/environment.yml](shared/environment.yml) | Conda environment setup |

**Essentials:**
- Authorship per project, following [CRediT](https://credit.niso.org/) taxonomy
- AI usage fully disclosed in each manuscript
- Zero tolerance for hallucinated citations
- No raw data in repo — only links and scripts
- Computation on local machines or rented servers
- This is an experiment, not a guarantee

## License

MIT License. See [LICENSE](LICENSE).

---

*10 experiments. Some will fail. All will be visible. If you want to find where AI's real boundary lies in scientific research, join us.*

*10 个实验。有的会失败。全部公开。想找到 AI 做科研的真实边界在哪里，来一起折腾。*
