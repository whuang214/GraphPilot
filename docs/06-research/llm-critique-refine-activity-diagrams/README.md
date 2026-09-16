# LADEX (critique–refine) — source material

Local copy of the paper that informs GraphPilot's **structural critique–refine loop** and the
**deterministic vs. LLM** split between generation and evaluation. Kept here for reference /
traceability. **Retrieved: 2026-07-02.**

- **[`findings.md`](./findings.md)** — full summary, design breakdown, and how the paper maps to
  GraphPilot (with pointers to the owning design docs).
- **[`ladex-khamsepour-2025.pdf`](./ladex-khamsepour-2025.pdf)** — the paper itself (details below).

Backs `docs/02-design-and-features/04-generation-design.md` ("Structural critique–refine loop")
and `docs/02-design-and-features/07-evaluation-and-doe-design.md`; the design choices in those docs
trace to the findings in [`findings.md`](./findings.md).

## The paper

| File | Source | Covers |
| --- | --- | --- |
| `ladex-khamsepour-2025.pdf` | https://arxiv.org/abs/2509.03463 (v2, 2025-11-27; PDF: https://arxiv.org/pdf/2509.03463v2) | Khamsepour, Cole, Ashraf, Tan, Puri, Sabetzadeh, Nejati — *The Impact of Critique on LLM-Based Model Generation from Natural Language: The Case of Activity Diagrams*. Introduces **LADEX** (LLM-based Activity Diagram Extractor), a critique–refine pipeline, and five ablated variants comparing algorithmic vs. LLM structural checks and the value of LLM semantic-alignment checks. ~1.9 MB. |

## Notes

- The **v2** PDF (2025-11-27) is committed here; the arxiv `abs` page links every version.
- Consistent with `docs/research/uml-sysml-vocabulary/`, the PDF is committed. If you'd rather
  not commit binaries, add `docs/research/llm-critique-refine-activity-diagrams/*.pdf` to `.gitignore` and keep
  it locally.
