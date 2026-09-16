# Answer-Key and Training-Fixture Design

## Purpose

GraphPilot keeps model-visible training examples and evaluator-only answer keys as different artifacts with different authority. This document owns the exact first-rollout training fixture set, deterministic derivation, author/reviewer sign-off, and the authoring firewall that prevents training or runtime generation from contaminating evaluation gold. The evaluation boundary, matcher, judge, runs, gates, and reports are owned by [`07-evaluation-and-doe-design.md`](../07-history/retired-evaluation-and-doe-design.md).

## Artifact classes and authority

| Artifact | Input → output | Visibility and consumer |
| --- | --- | --- |
| Direct training fixture | Complete `graphpilot.direct.diagram-request.v1` → direct logical diagram | Model-visible; direct generator only |
| Context training fixture | Complete `graphpilot.context.evidence-manifest.v1` + `graphpilot.context.diagram-request.v1` → grounded logical diagram with origins | Model-visible; context generator only |
| Built-in evaluation case and oracle | Frozen direct/context authority → independently authored equivalence oracle | Evaluator-only; never available to generation |
| RepoBench oracle | Frozen repository state + request → external benchmark oracle | Evaluator-only and outside the evaluated workspace |

A runtime generation tool never authors or revises its own training gold or evaluation gold. Direct examples never teach context grounding, context examples never borrow direct output, and no held-out oracle may enter a prompt, runtime example selector, generator workspace, or generation trace.

## Fixed V1 runtime policy

Every initial generation call receives exactly two fixed curated examples for its generation mode and diagram type:

| Diagram type | Direct examples | Context examples |
| --- | ---: | ---: |
| `activity_diagram` | 2 | 2 |
| `use_case_diagram` | 2 | 2 |
| `bdd_diagram` | 2 | 2 |

The foundational example is first and the advanced example is second. Selection is by one immutable ordered manifest per mode/type cell—not lexical matching, tags, embeddings, retrieval, or path sorting. Every generation input and trace records the exact set version, set digest, and ordered example IDs. Missing, corrupt, substituted, reordered, or dropped examples fail before the provider call. The pair is indivisible: GraphPilot never trims examples to fit a budget. Generation repair and semantic repair packets contain no examples. Readiness uses no runtime few-shot examples.

## Source and derived artifact model

A direct source fixture contains:

```text
request.gp-request.json
expected.logical.json
output.gp.json
metadata.json
```

A context source fixture contains:

```text
evidence.gp-evidence.json
request.gp-request.json
expected.logical.json
output.gp.json
metadata.json
```

The author hand-writes the request authority and `expected.logical.json`. For context, the author also hand-writes JSON 1 and every smallest-sufficient origin against the request allowlist. The following are deterministic derivations and are never independently edited:

```text
validated source fixture
  -> populated mode-specific generation input
  -> compact graphpilot.<mode>.generation-example.v1 {input, output}
  -> conformed canonical output.gp.json
  -> PyGraphviz layout
  -> validated/rendered SVG and gallery entry
```

A digest mismatch between source and any derived artifact fails fixture verification. The shared runtime wrapper is `{input, output}`, but direct and context example schemas, pools, validators, authority, and origin rules remain separate.

The source layout is mode-explicit:

```text
backend/assets/blueprints/<type>/
  direct-examples/training/<example-id>/
  context-examples/training/<example-id>/
```

Evaluation fixtures may use the same complete source shape under evaluator-owned storage, but their gold is never projected into a runtime example.

## Metadata and sign-off

Every `metadata.json` uses `graphpilot.generation.training-fixture-metadata.v1` / `generationTrainingFixtureMetadata` and records:

- `exampleId`, `mode`, `diagramType`, and `level: foundational|advanced`;
- one to sixteen unique `domainTags` and `structureTags`;
- nonblank `author` and `authoredAt`;
- a different nonblank `reviewer`, `reviewedAt`, and `reviewStatus: approved`;
- exact request, logical-schema, and semantic-profile versions; and
- canonical input and output digests.

Approval requires distinct independently executed author and reviewer identities; the author cannot approve the fixture. For machine-authored training fixtures, stateless agent roles are recorded honestly rather than represented as people. Automated checks establish contract and graph validity; the independent reviewer owns semantic acceptance and confirms authority fidelity, realism, abstraction, relationship direction, containment, structured fields, absence of unsupported meaning, and—for context—origin relevance and minimality. Approval occurs only after canonical validation, PyGraphviz layout, canvas/SVG gallery review, and round-trip checks pass. Hidden certification gold retains its separate human-independence policy.

## Six immutable ordered manifests

Each manifest uses `graphpilot.generation.training-example-set.v1` / `generationTrainingExampleSet`, fixes one generation mode and one diagram type, and contains exactly two ordered references. Each reference records the example ID, fixture-metadata digest, runtime-input digest, and runtime-output digest; the manifest records its canonical set digest.

| Set version | Ordered example IDs |
| --- | --- |
| `graphpilot.direct.training-examples.activity.v1` | `parcel-locker-pickup`, `device-repair-assessment` |
| `graphpilot.context.training-examples.activity.v1` | `return-authorization`, `multi-channel-alert-delivery` |
| `graphpilot.direct.training-examples.use-case.v1` | `pet-care-appointment-portal`, `makerspace-access-system` |
| `graphpilot.context.training-examples.use-case.v1` | `volunteer-shift-portal`, `equipment-maintenance-portal` |
| `graphpilot.direct.training-examples.bdd.v1` | `camping-stove-specification`, `digital-publishing-platform` |
| `graphpilot.context.training-examples.bdd.v1` | `irrigation-controller`, `laboratory-analyzer-platform` |

Changing one fixture creates a new immutable version only for its mode/type set. A runtime call cannot mix versions or partially replace a set.

## Exact direct fixtures

### Activity: Parcel Locker Pickup (foundational)

Authority requires scanning and validating a pickup code, unlocking and collecting on a valid code, denying access on an invalid code, explicit guards, and both outcomes. Delivery into the locker, hardware internals, and support-case processing are excluded.

```text
Start -> Scan Pickup Code -> Validate Pickup Code -> Code Valid?
Code Valid? -- code is valid --> Unlock Locker -> Collect Parcel -> Pickup Complete
Code Valid? -- code is invalid --> Deny Access -> Access Denied
```

The graph has one `initialNode`, one `decisionNode`, two `activityFinalNode`s, and no unnecessary merge or concurrency.

### Activity: Device Repair Assessment (advanced)

Authority requires receipt before assessment; concurrent hardware diagnostics and warranty checking; synchronization before eligibility; and covered-repair versus quotation outcomes. Inventory, customer communication, and repair-execution detail are excluded.

```text
Start -> Receive Device -> Fork
Fork -> Run Hardware Diagnostics -> Join
Fork -> Check Warranty -> Join
Join -> Covered Repair?
Covered Repair? -- covered --> Schedule Repair -> Assessment Complete
Covered Repair? -- not covered --> Prepare Quotation -> Assessment Complete
```

The fork has one incoming edge and distinct targets; the join has distinct sources and one outgoing edge; the decision occurs after synchronization.

### Use case: Pet Care Appointment Portal (foundational)

The subject is `Pet Care Appointment Portal`. External actors are `Pet Owner` and `Receptionist`. Contained use cases are `Book Appointment`, `Check Availability`, `View Upcoming Appointments`, and `Manage Clinic Schedule`.

```text
Pet Owner -> Book Appointment                         association
Pet Owner -> View Upcoming Appointments               association
Receptionist -> Manage Clinic Schedule                association
Book Appointment -> Check Availability                include
```

Payments and medical records are excluded. Actors remain outside the subject, use cases carry the subject `parentId`, and include points from the base use case to the mandatory reused use case.

### Use case: Makerspace Access System (advanced)

The subject is `Makerspace Access System`. Actors are `Member`, `Sponsored Member`, and `Safety Officer`. Contained use cases are `Enter Workshop`, `Verify Certification`, `Request After-Hours Access`, and `Approve After-Hours Request`. `Enter Workshop` declares extension point `access-window`.

```text
Member -> Enter Workshop                                      association
Member -> Request After-Hours Access                          association
Safety Officer -> Approve After-Hours Request                 association
Enter Workshop -> Verify Certification                        include
Request After-Hours Access -> Approve After-Hours Request     include
Request After-Hours Access -> Enter Workshop                  extend
  condition: sponsor approval exists
  extensionLocations: [access-window]
Sponsored Member -> Member                                    generalization
```

Payment and equipment maintenance are excluded. The extending use case points to the base; the specialized actor points to its parent.

### BDD: Camping Stove Specification (foundational)

The fixture contains exactly one visible `block`, `Camping Stove`, and no edges or separately defined property-type Blocks. Its strict feature arrays contain:

```text
properties:
  part burner: Burner [1]
  part fuelCanister: Fuel Canister [1]
  part potSupports: Pot Support [3]
  value massKg: Real = 0.45
  value maximumHeatOutputKw: Real = 3.2
  flow fuel: Fuel direction=in
operations:
  ignite()
  shutdown()
constraints:
  positive-output: maximumHeatOutputKw > 0
```

Multiplicities use `{lower, upper}` and defaults are JSON values, not text embedded in type names. Empty strict feature arrays remain present.

### BDD: Digital Publishing Platform (advanced)

Six Blocks represent `Content Processor`, `Text Processor`, `Image Processor`, `Publishing Pipeline`, `Rights Service`, and `Publication`. `Content Processor` is abstract and owns `process(content: Publication)`.

```text
Text Processor -> Content Processor             generalization
Image Processor -> Content Processor            generalization
Content Processor -> Publishing Pipeline        composition (part -> whole)
Publishing Pipeline -> Rights Service           dependency (client -> supplier)
Publishing Pipeline -> Publication              association
```

The association ends name `pipeline` and `publications` with multiplicities `1` and `0..*`. Deployment and persistence internals are excluded.

## Exact context fixtures

Every context node and edge has a smallest-sufficient `origin`; exact claim versions and assumptions are selected and allowlisted. The only schema-rule origin is `activity.initial-node`, and it applies only to a neutral initial node. No context example ID or claim ID authorizes output for an actual request unless that exact reference appears in the actual request allowlist.

### Activity: Return Authorization (foundational)

Selected authority establishes request receipt, return-window eligibility, label issuance, and rejection. There are no assumptions.

```text
Start [activity.initial-node]
  -> Receive Return Request [claim-return-request-received]
  -> Check Return Eligibility [claim-return-eligibility-window]
  -> Eligible? [claim-return-eligibility-window]
Eligible? -- eligible --> Issue Return Label -> Label Issued
  [eligibility + label-issued claims as needed]
Eligible? -- ineligible --> Reject Return -> Return Rejected
  [eligibility + rejected claims as needed]
```

Every edge cites only the claim set needed for its exact transition. No final-node schema rule exists.

### Activity: Multi-Channel Alert Delivery (advanced)

Selected claims establish recipient loading, concurrent email/SMS work, one email retry, synchronization, and combined-result recording. Accepted assumption `assumption-alert-missing-mobile-skip` says that a missing mobile number produces an SMS skip rather than a failure.

```text
Start [schema] -> Load Recipients -> Delivery Fork
Delivery Fork -> Send Email -> Email Success?
Email Success? -- delivered --> Email Merge
Email Success? -- transient failure --> Retry Email -> Email Merge
Delivery Fork -> Has Mobile Number?
Has Mobile Number? -- yes --> Send SMS -> SMS Merge
Has Mobile Number? -- no --> Skip SMS -> SMS Merge
Email Merge -> Delivery Join
SMS Merge -> Delivery Join
Delivery Join -> Record Combined Result -> Complete
```

All decision edges have guards. Merge nodes recombine alternatives; only the join synchronizes channels. Origins use the concurrent-channel, operation, retry, result, and accepted-assumption authority only where each is needed.

### Use case: Volunteer Shift Portal (foundational)

Selected claims establish the subject, Volunteer and Coordinator roles, view/sign-up/cancel/publish capabilities, and mandatory capacity checking. All use cases are contained by `Volunteer Shift Portal`.

```text
Volunteer -> View Available Shifts                association
Volunteer -> Sign Up for Shift                    association
Volunteer -> Cancel Signup                        association
Coordinator -> Publish Shift                      association
Sign Up for Shift -> Check Shift Capacity         include
```

Each subject, actor, use case, association, and include edge cites its exact boundary/role/capability/reuse claim. No neutral unsupported element is permitted.

### Use case: Equipment Maintenance Portal (advanced)

Selected claims establish the subject; Operator, Technician, Senior Technician, and Maintenance Administrator; fault reporting/diagnosis/history/escalation/scheduling; and actor specialization. `Diagnose Fault` declares `diagnosis-outcome`.

```text
Operator -> Report Fault                                   association
Technician -> Diagnose Fault                               association
Maintenance Administrator -> Schedule Preventive Maintenance association
Diagnose Fault -> Retrieve Maintenance History             include
Escalate Emergency Repair -> Diagnose Fault                extend
  condition: diagnosis is critical
  extensionLocations: [diagnosis-outcome]
Senior Technician -> Technician                            generalization
```

Every element cites the exact role, capability, or relationship claim that authorizes it.

### BDD: Irrigation Controller (foundational)

Selected claims establish `Irrigation Controller`, `Moisture Sensor`, and `Valve`; owned sensors and valves at `1..*`; a sample interval; and a sensor/valve association.

```text
Irrigation Controller properties:
  part sensors: Moisture Sensor [1..*]
  part valves: Valve [1..*]
  value sampleIntervalSeconds: Integer

Moisture Sensor -> Irrigation Controller     composition
Valve -> Irrigation Controller               composition
Moisture Sensor -> Valve                     association
```

The controller node aggregates only the definition/property claims needed for its rows. Relationship end roles and multiplicities match claim meaning; no per-property origin field is invented.

### BDD: Laboratory Analyzer Platform (advanced)

Selected claims establish Analyzer, Sample Tray, Measurement Module, Optical Module, Chemical Module, Calibration Service, and Result Repository; ownership, specialization, calibration dependency, repository association, and `measure()`. Accepted assumption `assumption-analyzer-four-module-cap` bounds installed measurement modules at four.

```text
Analyzer properties:
  part sampleTray: Sample Tray [1]
  part measurementModules: Measurement Module [1..4]
Measurement Module operation: measure()

Sample Tray -> Analyzer                         composition
Measurement Module -> Analyzer                 composition
Optical Module -> Measurement Module           generalization
Chemical Module -> Measurement Module          generalization
Analyzer -> Calibration Service                dependency
Analyzer -> Result Repository                  association
```

The Analyzer origin cites the cap assumption only for the node carrying `[1..4]`. Every target is an emitted Block definition and every origin remains smallest-sufficient.

## Fixture verification gates

Every fixture must pass all of these gates:

1. Source authority validates under its exact namespace-first contract; IDs and references are unique and current.
2. Logical gold validates against its exact mode/type strict schema and uses only the canonical generation core.
3. Direct logical output rejects origins; every context node and edge has one valid origin.
4. Context references are selected, accepted, and allowlisted; schema-only grounding is limited to a neutral Activity initial node.
5. Endpoint, direction, containment, decision/fork/join, multiplicity, structured-field, and reachability rules pass.
6. Runtime pairs and canonical outputs derive from source and match recorded digests.
7. PyGraphviz layout, canonical validation, canvas/SVG parity, rendering, and round-trip checks pass.
8. The distinct reviewer approves semantic fidelity, realism, abstraction, unsupported-addition absence, and context origin minimality.
9. Manifest order and digest match exactly; no training, hidden-evaluation, visible-calibration, or RepoBench identity overlaps.

## Evaluation-gold firewall

Training is finalized before hidden evaluation authoring begins. The generator, prompts, schemas, semantic-review behavior, examples, evaluator, matcher, judge rubric, reports, and gate thresholds freeze before independent authors receive hidden slots. Prompt/training authors cannot author or approve hidden gold. Every hidden case has a separate author, reviewer, and adjudicator, and gold remains outside the production package and model-visible workspace.

Visible synthetic and human-labeled calibration fixtures may exercise schemas, derivation, matcher behavior, embeddings, judge responses, reports, and failure attribution. They are never training examples and never hidden quality evidence. The future built-in suite contains 48 independently authored hidden cases—eight per mode/type cell—and no hidden pilot. If hidden results cause a generator or evaluator change, that set becomes historical and a new independent set is required. See [`07-evaluation-and-doe-design.md`](../07-history/retired-evaluation-and-doe-design.md) for exact run and certification policy.

## Related owners

- [`04-generation-design.md`](07-generation.md) — shared generation phases, model packets, semantic review, and layout.
- [`07-evaluation-and-doe-design.md`](../07-history/retired-evaluation-and-doe-design.md) — evaluation cases/oracles, capture, matcher, judge, gates, reports, runs, and leakage enforcement.
- [`08-context-backed-generation/`](01-context-generation/README.md) — JSON 1/JSON 2 authority, readiness, context generation, origins, and trace behavior.
- [`02-validation-design.md`](05-validation.md) and [`03-rendering-design.md`](06-rendering.md) — canonical validation and rendering contracts used by fixture proof.
