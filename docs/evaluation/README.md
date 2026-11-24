# Small evaluation protocol

Use this for a profile change, workflow or skill candidate. The objective is comparable evidence, not a benchmark platform. Keep candidate acceptance separate from a passed local fixture.

## Run a comparison

1. **Define the claim and case.** State the observed gap, task class (simple, normal or complex by risk), fixed input or repository commit, concrete deliverable and pass/fail criteria. Pick relevant cases, usually one routine case, one normal case and one high-risk or failure case when the change affects those paths. Reuse the same source and acceptance checks.
2. **Choose baseline and variant.** For a skill, compare the lean workflow alone with the same task plus the candidate; for a profile compare the same workflow and role scope with different explicit configurations. Reset to the same starting commit or input. Hold client version, tools, permissions, model/effort (except the tested variable), context and time constraints constant where practical. Note deviations. Do not install unrelated skills or change an existing project as an experiment.
3. **Test discovery separately.** Validate the candidate package/metadata. Start fresh contexts: one natural prompt that should activate, one explicit invocation, one similar prompt that should not activate. For example, a clarification candidate should select on “The outcome is unclear; help decide what matters before we proceed,” but not on “Correct this already-approved heading.” Adapt prompts to the actual trigger. Capture host traces when available. Manual invocation and the agent saying it ran are not evidence of natural selection. If the host cannot expose a trace, record selection as uncertain even if behaviour looks correct.
4. **Run both conditions.** Keep the same task input and test criteria. Capture result artifacts, actual acceptance checks, material omissions, questions/interruptions, reviewer findings, correction cycles and completion status. When process discipline is the claim, define observable required steps and a stopping condition before the run; compare skipped steps, unnecessary detours, scope drift, premature or late completion, and user redirects. Do not reward mechanical steps that add no value. Prefer an independent reviewer unaware of which variant produced the artifact where possible. Repeat noisy/close comparisons before generalising.
5. **Record routing and total cost.** For each phase and role, log requested model/effort, any override or fallback, configured/spawn-confirmed/runtime-verified state and evidence. Count coordinator plus delegates and retries/reviews. Record input/output tokens, reasoning and cached tokens if separately exposed, repeated context or cache observations, elapsed wall time and credit or API charge where available. Avoid double-counting totals or assuming missing quantities are zero. Record the source and unit of each metric. Subscription usage/credits and API pricing are distinct; report both only with evidence. If only session totals exist, label their scope rather than allocate them to agents without evidence.
6. **Decide.** Compare acceptance and cost per completed task, not just individual calls. A cheaper result with lost acceptance is not a success. Record the result as keep, revise, reject or inconclusive, with the next smallest test. Package validation, selection, behaviour, incremental benefit, cost and user acceptance each have their own status. A skill remains candidate/pilot until independent review and explicit user acceptance. Do not claim savings from a fixture or from missing telemetry.

Use the [result template](result-template.md) per comparison. A [local example](profile-fixture-example.md) demonstrates the record with an actual configuration test, not a live model evaluation. Preserve raw evidence privately when necessary; only publish sanitized summaries and permitted links.

## What to compare for the ACS pilot (#5)

| Case | Same acceptance criteria for both profiles |
| --- | --- |
| Simple | Correct local change, focused verification, no unnecessary delegation or plan |
| Normal | Bounded behaviour implemented, focused tests, documentation impact, independent review |
| Complex | Risk addressed, appropriate plan/scope, required tests and independent review, correction/escalation boundary observed |

Use the same cases across comparable host/profile runs. Do not compare Claude credits directly to Codex credits as if interchangeable.

Optional hook records from #16 can supplement the pilot: see [hook event scope and limitations](../hooks.md). Keep model requests, spawn notifications, configured capability versions and actual runtime evidence distinct. Record missing usage as unknown; do not add session totals to per-attempt counters or assume that an API cost estimate is a subscription charge.
