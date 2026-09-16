# First-Rollout Training Fixture Specification

> **Status: mechanical fixture specification under the approved twelve-scenario policy.** This document defines the
> exact authority/topology/origin intent the distinct fixture author and reviewer must turn into formal source files.
> It does not author or reserve held-out evaluation cases.

## Shared fixture shape

Direct fixture:

```text
request.gp-request.json
expected.logical.json
output.gp.json
metadata.json
```

Context fixture:

```text
evidence.gp-evidence.json
request.gp-request.json
expected.logical.json
output.gp.json
metadata.json
```

The expected logical object is hand-authored. The compact runtime `{input, output}` example, populated generation
input, canonical output, and SVG are derived deterministically and never edited independently.

## Metadata contract

```text
schemaVersion: graphpilot.generation.training-fixture-metadata.v1
kind: generationTrainingFixtureMetadata
exampleId: lower kebab, max 128
mode: direct|context
diagramType: activity_diagram|use_case_diagram|bdd_diagram
level: foundational|advanced
domainTags: 1..16 unique lower kebab
structureTags: 1..16 unique lower kebab
author: nonblank max 128
authoredAt: UTC timestamp
reviewer: nonblank max 128 and different from author
reviewedAt: UTC timestamp
reviewStatus: approved
requestSchemaVersion
logicalSchemaVersion
semanticProfileVersion
inputDigest
outputDigest
```

Approval occurs only after source/derived schema validation, current-core enforcement, deterministic graph checks,
context provenance validation, PyGraphviz layout, canonical validation, canvas/SVG gallery review, and semantic
review against authority.

## Ordered set manifests

Each manifest uses `schemaVersion=graphpilot.generation.training-example-set.v1`,
`kind=generationTrainingExampleSet`, one `generationMode`, one `diagramType`, exactly two ordered example refs, and a
canonical set digest. Each ref contains example ID, fixture metadata digest, runtime input digest, and runtime output
digest.

| Set version | Ordered examples |
| --- | --- |
| `graphpilot.direct.training-examples.activity.v1` | `parcel-locker-pickup`, `device-repair-assessment` |
| `graphpilot.context.training-examples.activity.v1` | `return-authorization`, `multi-channel-alert-delivery` |
| `graphpilot.direct.training-examples.use-case.v1` | `pet-care-appointment-portal`, `makerspace-access-system` |
| `graphpilot.context.training-examples.use-case.v1` | `volunteer-shift-portal`, `equipment-maintenance-portal` |
| `graphpilot.direct.training-examples.bdd.v1` | `camping-stove-specification`, `digital-publishing-platform` |
| `graphpilot.context.training-examples.bdd.v1` | `irrigation-controller`, `laboratory-analyzer-platform` |

## Direct activity — Parcel Locker Pickup

Authority:

```text
goal: Model customer pickup with explicit valid/invalid outcomes.
included: scan code, validate code, unlock/collect, deny access, both outcomes
excluded: delivery into locker, hardware internals, support-case processing
requirements:
  requirement-scan-code       behaviorStep  Customer scans the pickup code.
  requirement-validate-code   behaviorStep  The system validates the code.
  requirement-valid-outcome   behaviorStep  A valid code unlocks the locker and the customer collects the parcel.
  requirement-invalid-outcome behaviorStep  An invalid code denies access.
  requirement-guards          constraint    Both decision branches carry explicit guards.
```

Logical nodes:

| ID | Type | Label |
| --- | --- | --- |
| `start` | `initialNode` | `Start` |
| `scan-code` | `opaqueAction` | `Scan Pickup Code` |
| `validate-code` | `opaqueAction` | `Validate Pickup Code` |
| `code-valid` | `decisionNode` | `Code Valid?` |
| `unlock-locker` | `opaqueAction` | `Unlock Locker` |
| `collect-parcel` | `opaqueAction` | `Collect Parcel` |
| `deny-access` | `opaqueAction` | `Deny Access` |
| `pickup-complete` | `activityFinalNode` | `Pickup Complete` |
| `access-denied` | `activityFinalNode` | `Access Denied` |

Logical edges:

```text
start -> scan-code
scan-code -> validate-code
validate-code -> code-valid
code-valid -> unlock-locker       guard: code is valid
code-valid -> deny-access         guard: code is invalid
unlock-locker -> collect-parcel
collect-parcel -> pickup-complete
deny-access -> access-denied
```

Coverage: foundational sequence, one guarded decision, two explicit outcomes, no unnecessary merge/concurrency.

## Direct activity — Device Repair Assessment

Authority:

```text
goal: Assess a received device with synchronized diagnostics and warranty work before choosing covered repair or quote.
included: receive device, hardware diagnostics, warranty check, synchronization, eligibility decision, repair/quote
excluded: inventory, customer communication, repair execution details
requirements:
  requirement-receive-device   behaviorStep  Receive the device before assessment.
  requirement-parallel-checks  behaviorStep  Hardware diagnostics and warranty checking execute concurrently.
  requirement-synchronize      constraint    Both checks synchronize before eligibility is decided.
  requirement-covered-repair   behaviorStep  Covered devices schedule repair.
  requirement-quotation        behaviorStep  Other devices receive a quotation.
```

Logical nodes:

```text
start initialNode Start
receive-device opaqueAction Receive Device
assessment-fork forkNode Fork
hardware-diagnostics opaqueAction Run Hardware Diagnostics
check-warranty opaqueAction Check Warranty
assessment-join joinNode Join
covered decisionNode Covered Repair?
schedule-repair opaqueAction Schedule Repair
prepare-quotation opaqueAction Prepare Quotation
assessment-complete activityFinalNode Assessment Complete
```

Logical edges:

```text
start -> receive-device
receive-device -> assessment-fork
assessment-fork -> hardware-diagnostics
assessment-fork -> check-warranty
hardware-diagnostics -> assessment-join
check-warranty -> assessment-join
assessment-join -> covered
covered -> schedule-repair       guard: covered
covered -> prepare-quotation     guard: not covered
schedule-repair -> assessment-complete
prepare-quotation -> assessment-complete
```

Coverage: one incoming/distinct fork targets, distinct join sources/one outgoing, guarded post-join decision.

## Direct use case — Pet Care Appointment Portal

Authority:

```text
goal: Show pet-owner appointment behavior and receptionist schedule management.
included: Pet Owner, Receptionist, booking, availability, upcoming appointments, clinic schedule
excluded: payments, medical records
requirements:
  requirement-pet-owner       entity        Pet Owner is an external actor.
  requirement-receptionist    entity        Receptionist is an external actor.
  requirement-book            actorGoal     Pet Owner books an appointment.
  requirement-availability    capability    Booking always includes checking availability.
  requirement-view            actorGoal     Pet Owner views upcoming appointments.
  requirement-manage-schedule actorGoal     Receptionist manages the clinic schedule.
  requirement-subject         boundary      Use cases appear inside Pet Care Appointment Portal.
```

Nodes:

```text
pet-care-portal subject Pet Care Appointment Portal
pet-owner actor Pet Owner
receptionist actor Receptionist
book-appointment useCase Book Appointment parentId=pet-care-portal
check-availability useCase Check Availability parentId=pet-care-portal
view-appointments useCase View Upcoming Appointments parentId=pet-care-portal
manage-schedule useCase Manage Clinic Schedule parentId=pet-care-portal
```

Edges:

```text
pet-owner -> book-appointment association
pet-owner -> view-appointments association
receptionist -> manage-schedule association
book-appointment -> check-availability include
```

Coverage: optional subject shown correctly, actors outside, contained use cases, minimal include direction.

## Direct use case — Makerspace Access System

Authority:

```text
goal: Show certification, after-hours extension, approval, and actor specialization.
included: Member, Sponsored Member, Safety Officer, entry, certification, after-hours request/approval
excluded: payment, equipment maintenance
requirements:
  requirement-member-entry       actorGoal     Member enters the workshop.
  requirement-certification      relationship  Enter Workshop includes Verify Certification.
  requirement-after-hours        actorGoal     Member may request after-hours access.
  requirement-extension          relationship  Request After-Hours Access extends Enter Workshop when sponsor approval exists.
  requirement-extension-location property      Enter Workshop declares extension point access-window.
  requirement-approval           actorGoal     Safety Officer approves after-hours requests.
  requirement-specialization     relationship  Sponsored Member specializes Member.
```

Nodes:

```text
makerspace subject Makerspace Access System
member actor Member
sponsored-member actor Sponsored Member
safety-officer actor Safety Officer
enter-workshop useCase Enter Workshop parentId=makerspace extensionPoints=[access-window]
verify-certification useCase Verify Certification parentId=makerspace
request-after-hours useCase Request After-Hours Access parentId=makerspace
approve-after-hours useCase Approve After-Hours Request parentId=makerspace
```

Edges:

```text
member -> enter-workshop association
member -> request-after-hours association
safety-officer -> approve-after-hours association
enter-workshop -> verify-certification include
request-after-hours -> approve-after-hours include
request-after-hours -> enter-workshop extend condition="sponsor approval exists" extensionLocations=[access-window]
sponsored-member -> member generalization
```

Coverage: include/extend are distinct, extension location exists on target, specialized actor points to parent.

## Direct BDD — Camping Stove Specification

Authority requires exactly one visible `block`, no edges, and no separately defined property-type Blocks.

Node `camping-stove` has:

```text
semanticType: block
label: Camping Stove
features.properties:
  part burner: Burner [1]
  part fuelCanister: Fuel Canister [1]
  part potSupports: Pot Support [3]
  value massKg: Real = 0.45
  value maximumHeatOutputKw: Real = 3.2
  flow fuel: Fuel direction=in
features.operations:
  ignite()
  shutdown()
features.constraints:
  positive-output: maximumHeatOutputKw > 0
```

All multiplicities use `{lower, upper}`; defaults are values rather than embedded in type names. Empty feature arrays
remain present in strict logical output. Coverage: compact one-Block definition and internal feature compartments.

## Direct BDD — Digital Publishing Platform

Authority:

```text
goal: Show reusable processor specialization plus owned pipeline processing and external rights dependency.
included: Content Processor, Text/Image Processors, Publishing Pipeline, Rights Service, Publication
excluded: deployment, persistence internals
```

Nodes are six `block` definitions. `Content Processor` is abstract and owns a `process(content: Publication)`
operation. Relationships:

```text
text-processor -> content-processor generalization
image-processor -> content-processor generalization
content-processor -> publishing-pipeline composition
publishing-pipeline -> rights-service dependency
publishing-pipeline -> publication association
```

The composition models the processor definition as an owned pipeline role and points part → whole. Association end
data names `pipeline`/`publications` with multiplicities `1` and `0..*`. Coverage: all four core structural
relationships, operations, direction, and separate definitions only where materially useful.

## Context activity — Return Authorization

Selected claims:

```text
claim-return-request-received   behaviorStep  A return begins when the service receives a return request.
claim-return-eligibility-window constraint    Eligibility requires the purchase to be within the configured return window.
claim-return-label-issued       behaviorStep  Eligible returns receive a return shipping label.
claim-return-rejected           behaviorStep  Ineligible returns are rejected.
```

No assumptions. Allowlisted schema rule is only `activity.initial-node`.

Nodes and origins:

| ID/type/label | Smallest-sufficient origin |
| --- | --- |
| `start` / initialNode / Start | schema `activity.initial-node` only |
| `receive-request` / opaqueAction / Receive Return Request | `claim-return-request-received` |
| `check-eligibility` / opaqueAction / Check Return Eligibility | `claim-return-eligibility-window` |
| `eligible` / decisionNode / Eligible? | `claim-return-eligibility-window` |
| `issue-label` / opaqueAction / Issue Return Label | `claim-return-label-issued` |
| `reject-return` / opaqueAction / Reject Return | `claim-return-rejected` |
| `label-issued` / activityFinalNode / Label Issued | `claim-return-label-issued` |
| `return-rejected` / activityFinalNode / Return Rejected | `claim-return-rejected` |

Edges:

```text
start -> receive-request                 claim-return-request-received
receive-request -> check-eligibility     claim-return-request-received + claim-return-eligibility-window
check-eligibility -> eligible            claim-return-eligibility-window
eligible -> issue-label                  guard: eligible; claim-return-eligibility-window + claim-return-label-issued
eligible -> reject-return                guard: ineligible; claim-return-eligibility-window + claim-return-rejected
issue-label -> label-issued              claim-return-label-issued
reject-return -> return-rejected         claim-return-rejected
```

Every rationale states only the claim/schema-to-element mapping. No final-node schema rule exists.

## Context activity — Multi-Channel Alert Delivery

Selected claims:

```text
claim-alert-load-recipients       behaviorStep  Scheduler loads alert recipients.
claim-alert-concurrent-channels   relationship  Email and SMS channel work executes concurrently and later synchronizes.
claim-alert-send-email            behaviorStep  Email dispatcher attempts email delivery.
claim-alert-email-retry-once      behaviorStep  A transient email failure is retried once.
claim-alert-send-sms              behaviorStep  SMS dispatcher attempts SMS delivery.
claim-alert-record-combined       behaviorStep  Aggregator waits for both channel outcomes and records the combined result.
```

Accepted assumption:

```text
assumption-alert-missing-mobile-skip: A recipient without a mobile number produces an SMS skip, not a failure.
```

Topology:

```text
start(initial schema) -> load-recipients(claim-load) -> delivery-fork(claim-concurrent)

delivery-fork -> send-email(claim-email) -> email-success?(claim-retry)
email-success? -- delivered --> email-merge(claim-retry)
email-success? -- transient failure --> retry-email(claim-retry) -> email-merge

delivery-fork -> has-mobile-number?(assumption-skip)
has-mobile-number? -- yes --> send-sms(claim-sms) -> sms-merge(claim-sms + assumption-skip)
has-mobile-number? -- no --> skip-sms(assumption-skip) -> sms-merge

email-merge -> delivery-join(claim-concurrent + claim-record)
sms-merge -> delivery-join
delivery-join -> record-result(claim-record) -> complete(activityFinal, claim-record)
```

All decision edges have guards. Merge nodes recombine alternatives; only the join synchronizes the two distinct
channel branches. Every node/edge origin is the smallest sufficient claim/assumption set.

## Context use case — Volunteer Shift Portal

Selected claims include exact boundary, actor, capability, and mandatory-reuse meaning:

```text
claim-volunteer-portal-subject
claim-volunteer-role
claim-coordinator-role
claim-volunteer-view-shifts
claim-volunteer-sign-up
claim-volunteer-check-capacity
claim-volunteer-cancel-signup
claim-coordinator-publish-shift
```

Nodes:

```text
volunteer-portal subject Volunteer Shift Portal origin=subject claim
volunteer actor Volunteer origin=volunteer role
coordinator actor Coordinator origin=coordinator role
view-shifts useCase View Available Shifts parentId=volunteer-portal origin=view claim
sign-up useCase Sign Up for Shift parentId=volunteer-portal origin=sign-up claim
check-capacity useCase Check Shift Capacity parentId=volunteer-portal origin=capacity claim
cancel-signup useCase Cancel Signup parentId=volunteer-portal origin=cancel claim
publish-shift useCase Publish Shift parentId=volunteer-portal origin=publish claim
```

Edges:

```text
volunteer -> view-shifts association origin=view claim
volunteer -> sign-up association origin=sign-up claim
volunteer -> cancel-signup association origin=cancel claim
coordinator -> publish-shift association origin=publish claim
sign-up -> check-capacity include origin=sign-up + capacity claims
```

No neutral unsupported actor/use case/association is permitted and no use-case schema rule exists.

## Context use case — Equipment Maintenance Portal

Selected claims:

```text
claim-maintenance-portal-subject
claim-maintenance-operator-role
claim-maintenance-technician-role
claim-maintenance-senior-technician-specialization
claim-maintenance-administrator-role
claim-maintenance-report-fault
claim-maintenance-diagnose-fault
claim-maintenance-retrieve-history
claim-maintenance-critical-escalation
claim-maintenance-schedule-preventive
```

Nodes are grounded subject; Operator, Technician, Senior Technician, Maintenance Administrator actors; and Report
Fault, Diagnose Fault, Retrieve Maintenance History, Escalate Emergency Repair, Schedule Preventive Maintenance use
cases. Every use case has `parentId=maintenance-portal`.

Edges:

```text
operator -> report-fault association
technician -> diagnose-fault association
administrator -> schedule-preventive association
diagnose-fault -> retrieve-history include
escalate-emergency -> diagnose-fault extend
  condition: diagnosis is critical
  extensionLocations: [diagnosis-outcome]
senior-technician -> technician generalization
```

`Diagnose Fault` declares extension point `diagnosis-outcome`. Each node/edge cites its exact role/capability/
relationship claim; no neutral unsupported relationship is included.

## Context BDD — Irrigation Controller

Selected claims:

```text
claim-irrigation-controller-definition
claim-irrigation-moisture-sensor-definition
claim-irrigation-valve-definition
claim-irrigation-owns-sensors       multiplicity 1..*
claim-irrigation-owns-valves        multiplicity 1..*
claim-irrigation-sample-interval
claim-irrigation-sensor-valve-link
```

Nodes:

```text
irrigation-controller block
  part sensors: Moisture Sensor [1..*]
  part valves: Valve [1..*]
  value sampleIntervalSeconds: Integer
moisture-sensor block
valve block
```

The controller node origin aggregates only the definition/property claims needed for its feature rows. Sensor and
Valve nodes cite their definition claims. Relationships:

```text
moisture-sensor -> irrigation-controller composition origin=owns-sensors
valve -> irrigation-controller composition origin=owns-valves
moisture-sensor -> valve association origin=sensor-valve-link
```

Relationship end roles/multiplicities correspond to claim meaning. No per-property origin field is invented; origin
remains on the owning node/edge contract.

## Context BDD — Laboratory Analyzer Platform

Selected claims:

```text
claim-analyzer-definition
claim-sample-tray-definition
claim-measurement-module-definition
claim-optical-module-definition
claim-chemical-module-definition
claim-calibration-service-definition
claim-result-repository-definition
claim-analyzer-owns-sample-tray
claim-analyzer-owns-modules
claim-optical-specializes-module
claim-chemical-specializes-module
claim-analyzer-calibration-dependency
claim-analyzer-result-repository
claim-module-measure-operation
```

Accepted assumption:

```text
assumption-analyzer-four-module-cap: An analyzer supports at most four installed measurement modules.
```

Nodes are Analyzer, Sample Tray, Measurement Module, Optical Module, Chemical Module, Calibration Service, and Result
Repository, all as `block`. Analyzer features include `sampleTray: Sample Tray [1]` and
`measurementModules: Measurement Module [1..4]`; the upper bound cites the accepted assumption through the Analyzer
node origin. Measurement Module exposes `measure()`.

Relationships:

```text
sample-tray -> analyzer composition
measurement-module -> analyzer composition
optical-module -> measurement-module generalization
chemical-module -> measurement-module generalization
analyzer -> calibration-service dependency
analyzer -> result-repository association
```

Every node/edge has one smallest-sufficient claim/assumption origin. Dependency and association targets are emitted
Block definitions, not undeclared IDs.

## Fixture verification matrix

For every fixture:

1. Source authority validates and all IDs are unique/current.
2. Logical gold validates against its exact mode/type strict schema.
3. Direct output contains no origins; every context node/edge has one valid origin.
4. Context refs are selected/accepted/allowlisted and schema-only grounding is limited to neutral initial node.
5. Graph-level endpoint, direction, containment, decision/fork/join, multiplicity, and reachability rules pass.
6. Runtime pair is derived from the source fixture and matches its recorded digests.
7. PyGraphviz layout, canonical validation, canvas/SVG rendering, and round-trip checks pass.
8. Distinct reviewer confirms authority fidelity, realism, abstraction, no unsupported additions, and origin minimality.
9. Manifest order and set digest match exactly; no held-out/RepoBench identity overlaps.
