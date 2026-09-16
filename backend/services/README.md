# `services/`

The shared application core. Both entry points — the Django API for the browser and the
FastMCP server for the IDE — are thin adapters over these packages.

**No package here calls a provider.** The host authors a diagram
[draft](../../docs/03-design/01-generation/01-draft.md); the backend materializes it
deterministically.

## Import convention

Absolute imports from the `services` root:

```python
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
```

Dependency direction is one-way, and there is no cycle:

```text
shared + diagrams/catalog
  -> diagrams/{validation,layout,persistence,rendering}
  -> drafts
  -> materialization
  -> api/ and mcp_server/
```

## Layout

```text
services/
├── shared/            cross-domain plumbing
├── diagrams/          the diagram domain
│   ├── catalog/       types, element catalog, profiles, constants
│   ├── validation/    canonical validation and the structural critic
│   ├── layout/        PyGraphviz positions and sizing
│   ├── persistence/   validation-gated canonical writes
│   └── rendering/     SVG and PNG
├── drafts/            host draft validation, evidence, authoring contract
└── materialization/   draft -> logical -> canonical
```

## `shared/` — cross-domain plumbing

| Module | Owns |
| --- | --- |
| `workspace_storage_service.py` | Workspace resolution, path containment, bounded reads, atomic writes |
| `schema_registry.py` | Loading, caching, meta-validating, and `$ref`-resolving bundled schemas |
| `schema_identities.py` | Immutable contract identities and layout configuration versions |
| `canonical_json.py` | Deterministic serialization and digesting |
| `diagram_type_service.py` | Supported types and their human-readable meanings |
| `operation_problem.py` | The shared typed failure contract and its retryability table |

## `diagrams/` — the diagram domain

`catalog/` is the single source of the semantic vocabulary: which node and edge types each
diagram type permits, per-type defaults, notation family, primitives, and sizing. Validation,
layout, materialization, rendering, and the frontend catalog all derive from it.

`validation/` holds `DiagramValidationService` — pure, deterministic, non-mutating, and the
only producer of a `ValidationResult`. `persistence/` is the validated-write funnel every
canonical create and overwrite crosses. `layout/` runs pinned in-process PyGraphviz with no
fallback engine. `rendering/` produces SVG and PNG at canvas parity.

## `drafts/` — host input

Validates a submitted draft (identity, endpoints, evidence references, assurance pairing,
per-type notation legality), reads and digests cited source regions, re-checks freshness,
and projects the draft schema into a host-facing authoring contract.

Draft validation is not canonical validation: it reads the *input a host submitted*, never
the document GraphPilot assembles.

## `materialization/` — draft to diagram

Pure functions: vocabulary conformance, feature normalization, relationship-end
construction, provenance encoding, and canonical assembly. No I/O, no randomness, no clock
beyond the metadata timestamp. Same draft, same diagram.

## Related

- Architecture and service ownership: [`03-backend.md`](../../docs/02-architecture/03-backend.md)
- Draft contract and materialization: [`01-generation/`](../../docs/03-design/01-generation/README.md)
- Canonical validation boundaries: [`03-validation/`](../../docs/03-design/03-validation/README.md)
