# BDD Readiness Rubric

> **Scope of this doc.** [`rubric.json`](rubric.json) is the single normative machine-readable `bdd_diagram`
> rubric contract. This file owns the human-readable explanation and summary, concept mappings, claim guidance,
> and validation invariants without redefining that contract. Common policy lives in
> [`../../02-policy-and-calculation.md`](../../03-policy-and-calculation.md); final notation lives in
> [`bdd-diagram-blueprints.md`](../../../../02-diagram-schemas/02-bdd-blueprints.md).

## Purpose

Determine whether selected JSON 1 claims and accepted JSON 2 assumptions establish the requested structural
subject, definitions or instances, features, and relationships without requiring the host to preselect final
GraphPilot types.

## Normative rubric contract

[`rubric.json`](rubric.json) is the single normative machine-readable `bdd_diagram` rubric contract. The
sections below explain and summarize that contract without redefining it.

## Facet summary and criteria explanation

| Facet | Mode | Weight | Applicability | Sufficient (`3`) | Strong (`4`) | Gap overrideable? |
| --- | --- | ---: | --- | --- | --- | --- |
| `structuralSubject` | Required | 3 | Always. | The structural subject, requested level, and inclusion/exclusion boundary are established well enough to select the definitions or instances that belong in the BDD without an essential scope ambiguity. | The structural subject, level, viewpoint, included definitions or instances, and exclusions are explicit, complete, unambiguous, and supported without assumptions. | No |
| `definitions` | Required | 4 | Always. | Every definition included by the confirmed request has a stable identity and enough role, purpose, and broad conceptual meaning for the generator to map it; every included instance specification has an established identity and classifier. A single supported definition satisfies this criterion when it is the complete requested subject. | Every included definition's identity, purpose, and requested conceptual distinction—and every included instance's identity and classifier—are explicit, complete, unambiguous, and supported without assumptions. | No |
| `structuralRelationships` | Conditional | 4 | The request asks for a connection, selected/indexed context explicitly connects in-scope definitions or instances, or a disposition includes one. | Every requested relationship and instance link has established endpoints and enough broad kind, direction, and end-role meaning to model the requested structure. | Every included relationship and instance link, endpoint, direction, end role, and requested structural distinction is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `ownership` | Conditional | 3 | The request asks for ownership/whole-part meaning, selected/indexed context states it, or a disposition includes it. | Every requested ownership distinction has established owner and part/reference endpoints plus enough composite, shared/reference, containment, property-role, and lifecycle meaning to model it correctly. | Every included owner, owned or referenced endpoint, owning end, property role, aggregation kind, containment boundary, and lifecycle implication is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `featuresAndTypes` | Conditional | 3 | The request asks for feature/slot detail, selected/indexed context assigns it, or a disposition includes it. | Every requested feature and instance slot has an established owner, identity, broad kind, and type, with each requested value, value type, direction, default, and modifier established well enough to model it. | Every included feature and instance slot, owner, name, kind, type, value, value type, direction, default, modifier, and local meaning is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `multiplicity` | Conditional | 2 | The request asks for cardinality, selected/indexed context states an allowed count/range, or a disposition includes one. | Every requested multiplicity is assigned to the relevant property or relationship end with established lower and upper bounds, including optional and unbounded cases where requested. | Every included property's and relationship end's lower bound, upper bound, optionality, exact-count or range meaning, and unbounded status is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `specializationAndDependencies` | Conditional | 2 | The request asks for specialization/dependency, selected/indexed context states one, or a disposition includes one. | Every requested specialization and dependency has established child/parent or client/supplier endpoints, direction, and enough broad meaning to model the relationship. | Every included specialization and dependency, endpoint role, direction, and requested inheritance or reliance distinction is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `portsInterfaces` | Conditional | 2 | The request asks for port/interface detail, selected/indexed context states an interaction point, or a disposition includes one. | Every requested port and interface interaction point has an established owner, identity, type, and broad role, with each requested provided/required, flow-direction, conjugation, and behavioral distinction established well enough to model it. | Every included port and interface interaction point, owner, identity, kind, type, provided/required feature, flow direction, conjugation, behavioral status, and interaction meaning is explicit, complete, unambiguous, and supported without assumptions. | Yes |
| `constraints` | Conditional | 2 | The request asks for constraint content, selected/indexed context states an in-scope constraint, or a disposition includes one. | Every requested constraint has an established constrained subject and usable rule or expression, with each requested parameter's identity, type, direction, unit/quantity meaning, and applicability established well enough to model it. | Every included constraint, constrained subject, expression, parameter, type, direction, unit, quantity meaning, and applicability condition is explicit, complete, unambiguous, and supported without assumptions. | Yes |

## Concept mapping and adequacy boundaries

- Facets judge supported concepts, not final GraphPilot semantic types. The generator maps definitions to core `block` nodes, requested features to structured Block data, ownership to part-to-whole `composition`, references to `association`, and specialization/dependency to their core relationships. Primary Block stereotypes remain a manual editor choice.
- An `instanceSpecification` does not create a separate readiness facet: its identity and classifier are judged
  by `definitions`; its slots, values, and value types by `featuresAndTypes`; and its links to other instances or
  definitions by `structuralRelationships`. Ownership, multiplicity, or another specialized facet also applies
  when the same supported concept meets that facet's explicit applicability conditions.
- One supported definition may be ready when it is the complete subject requested and both required facets
  reach `3`. No supplemental relationship, feature, ownership, port, or constraint is required merely to make
  the BDD appear richer.
- A selection that is too narrow for the goal, below requested detail, or unable to form the requested model is
  handled by the general `selection_misses_goal`, `detail_below_request`, or `selection_not_modelable` finding,
  not by requiring an additional BDD facet.
- BDD may define ports and interfaces, but internal connector networks between part usages remain outside this
  type and are never inferred as BDD edges.

## Claim-kind guidance

| Facet | Commonly relevant JSON 1 claim kinds |
| --- | --- |
| `structuralSubject` | `boundary`, `entity`, `relationship` |
| `definitions` | `entity`, `property`, `constraint` |
| `structuralRelationships` | `relationship`, `entity`, `property` |
| `ownership` | `relationship`, `property`, `entity` |
| `featuresAndTypes` | `property`, `entity`, `capability`, `constraint` |
| `multiplicity` | `property`, `relationship`, `constraint` |
| `specializationAndDependencies` | `relationship`, `entity` |
| `portsInterfaces` | `property`, `relationship`, `entity`, `capability` |
| `constraints` | `constraint`, `property`, `entity` |

Claim kind alone never establishes coverage; selected meaning must satisfy the exact criterion.

## Validation invariants

1. [`rubric.json`](rubric.json) parses and has the exact BDD envelope/version.
2. All nine facets appear once in canonical order with the preserved weights and minimum rating `3`.
3. `structuralSubject` and `definitions` are required with `kind: always`; all other facets are conditional and
   carry non-empty `appliesWhenAny`, `notApplicableWhenAll`, and `uncertainWhen` arrays.
4. Every facet has one description, exact `0` through `4` rating anchors, and its deterministic gap policy.
5. A single supported definition may be ready when it fully matches the confirmed request; broader inadequacy
   is expressed by general alignment, detail, or modelability findings.
6. Instance identity/classifier, slot/value/type, and link meaning map to `definitions`, `featuresAndTypes`, and
   `structuralRelationships`, respectively; no instance-only facet is introduced.
7. Internal connector topology is never invented as BDD structure.
8. The rubric never requires host-selected SysML types or relationship ends.

### Final definition

> BDD readiness means supported context establishes the requested structural subject and its definitions or
> instances, plus every relationship, ownership, feature, multiplicity, specialization/dependency, port/interface,
> or constraint concept made applicable by the explicit conditions; one definition can be sufficient when that is
> the complete aligned request.
