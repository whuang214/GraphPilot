# UML / SysML vocabulary — source material

Reference material behind the neutral **UML + SysML vocabulary extraction** in
[`vocabulary.md`](vocabulary.md). **Specs-only:** the OMG specs are the source of truth; Mermaid is
kept only as a notation cross-check (and as the tool that draws the doc's visuals). **Sources
retrieved 2026-07-02; the extraction was spec-verified 2026-07-08.**

## How this folder is organized (by authority)

Two tiers — higher tier wins on any conflict:

```
uml-sysml-vocabulary/
├── vocabulary.md              ← compiled output: the neutral UML+SysML vocabulary extraction
├── 01-normative-omg-specs/    ← the authority (OMG UML 2.5.1 + SysML 1.6) — source of truth
└── 02-tool-corroboration/     ← Mermaid notation cross-check (+ React Flow schema pulls)
```

- **Tier 1 — normative OMG specs** are the **source of truth** (metamodel + notation). The
  vocabulary in `vocabulary.md` is extracted **directly** from their diagram-element tables,
  notation clauses, and concrete classifier descriptions. Coverage is tracked by clause rather
  than by term-presence searches, which prove occurrence but not semantic classification or
  completeness.
- **Tier 2 — tool corroboration** is a cross-check only, never overriding the specs. Mermaid
  confirms notation/naming (and renders the doc's Mermaid visuals); the React Flow pulls are a
  **separate concern** — they document the JSON node/edge schema GraphPilot aligns to, not UML.

## Tier 1 — normative OMG specs (the authority) · `01-normative-omg-specs/`

| File | Source | Covers |
| --- | --- | --- |
| `01-normative-omg-specs/omg-uml-2.5.1.pdf` | https://www.omg.org/spec/UML/2.5.1/ (PDF) | OMG **UML 2.5.1** (formal/2017-12-05) — the full UML metamodel + notation. The authority for every UML element, relationship, and diagram type. ~18 MB. |
| `01-normative-omg-specs/omg-sysml-1.6.pdf` | https://www.omg.org/spec/SysML/1.6/ (PDF) | OMG **SysML 1.6** (formal/2019-11-01) — blocks, parts, ports, connectors, value/constraint properties, requirements + the requirement relations. ~16.6 MB. |

## Tier 2 — tool corroboration · `02-tool-corroboration/`

Fetched via the Context7 docs API. Plain-text doc excerpts — **corroboration only, not
authoritative.**

| File | Source | Covers |
| --- | --- | --- |
| `02-tool-corroboration/context7_mermaid-class-relationships.md` | mermaid `syntax/classDiagram.md` | class-diagram **relationships**: generalization/inheritance, composition, aggregation, association, dependency, realization, link (+ multiplicities, stereotypes, members). |
| `02-tool-corroboration/context7_mermaid-requirement.md` | mermaid `syntax/requirementDiagram.md` | SysML-style **requirement** node kinds + relations: satisfies, traces, contains, derives, refines, verifies, copies. |
| `02-tool-corroboration/context7_reactflow-v12-node.md` | reactflow.dev `api-reference/types/node` | React Flow **v12 Node** fields (id, position, data, type, width/height, measured, parentId, …). **JSON-schema alignment, not UML vocabulary.** |
| `02-tool-corroboration/context7_reactflow-v12-edge.md` | reactflow.dev `api-reference/types/edge` | React Flow **v12 Edge** fields (id, source, target, sourceHandle, markerStart/End, label, style, …). **JSON-schema alignment, not UML vocabulary.** |

## Compiled output

| File | What it is |
| --- | --- |
| [`vocabulary.md`](vocabulary.md) | The neutral, spec-first **UML + SysML visual-vocabulary extraction**: diagram taxonomy; symbols/containers; structured features and compartments; relationships; end labels/adornments; special-rendering constructs; provenance; and clause-level source traceability. Independent of GraphPilot's JSON schema (that mapping lives in the standard, `00-diagram-json-schema.md`). |

## Notes

- **Specs-only.** An earlier secondary reference (the `uml-diagrams.org` element inventory) and a
  PlantUML pull were used as scaffolding during initial extraction but have been **removed** — the
  UML per-type grouping is now checked directly against the OMG UML spec (see the "Spec-verified"
  note in `vocabulary.md`). The **OMG PDFs are the tiebreaker** on any disagreement.
- These PDFs are large (~34 MB total). If you'd rather not commit binaries, add
  `docs/research/uml-sysml-vocabulary/01-normative-omg-specs/*.pdf` to `.gitignore` and keep them
  locally.
- The Tier-2 `.md` files are lightweight snapshots of live pages (content as of the retrieval date;
  the live sources may change).
