# Adaptive coding workflow

This is the ACS contract. Verified cross-host execution and measured benefits remain pilot work. A skill is optional unless the active task explicitly requires it.

## Choose the needed path

Use the most downstream adequate artifact: active ticket, then spec, then conversation. Inspect relevant code before reopening a settled decision. Briefly state the task class and reason; risk overrides size.

| Class | Typical trigger | Required outcome |
| --- | --- | --- |
| Simple | Local, understood, reversible change with low behavioural risk | Implement, perform focused verification and documentation check, inspect the diff. |
| Normal | Bounded behaviour change with known interfaces and manageable uncertainty | Reuse or write a short plan, implement, run relevant tests, update affected docs, obtain independent review. |
| Complex | Material uncertainty or consequential security, data, migration, concurrency, or architecture risk | Resolve the blocking uncertainty; define acceptance/spec and split work if needed; implement, test, document, and independently review the affected risks. |

Examples: a spelling fix is simple; a bounded feature is normally normal; a one-line authorisation change can be complex. Reclassify when evidence changes the risk. Do not create a spec or ticket for every small edit, or require a complete plan/spec/tickets chain when adequate artifacts already exist.

## Execute within the scope

The coordinator owns the active contract and integration. Use the matching `acs-*` named delegate from the selected profile when available; check the [profile commands and host verification](../../docs/models.md#profile-commands) before first delegation. Delegate only for the benefits in the [model policy](../../docs/models.md). Independent review uses a reviewer who did not implement the change; independence does not require a more expensive model. Parallelise disjoint work; coordinate shared files explicitly.

Use the narrowest meaningful checks for changed behaviour and risks. TDD is useful for suitable logic changes and regression reproduction; it is not a mandatory skill or ceremony. Run broader checks for an affected integration risk or a required repository gate. Do not repeat successful testing without a concrete reason. State unavailable checks as unrun.

For every task, ask which documentation the change makes stale: user instructions, configuration, APIs, operations, setup guidance, or consequential decisions. Update the relevant existing source in the same change, or state why no documentation change is needed. Record an ADR only for a consequential trade-off or a decision that would otherwise be difficult to understand; do not manufacture ADRs for routine edits.

## Review and correction boundary

Normal and complex behaviour changes need independent review against acceptance criteria and affected risks. Simple, documentation-only, and mechanical changes normally need coordinator inspection. A configuration change that alters behaviour is classified by its effect, not its filename. Report whether review was independent; if that capability is unavailable, do not label self-review as independent or the gate as passed.

Allow at most one substantial correction cycle after the first independent review. Initial implementation and its own test fixes do not consume this budget. A missing acceptance criterion, incorrect behaviour, violated guardrail, or missing necessary test is substantial. Style preferences alone do not trigger another cycle.

Correct the actionable findings, verify the affected behaviour, and have the correction reviewed. If substantial findings remain, or the failure reveals a material scope/architecture decision or recurring structural problem, report the evidence and ask for the required decision. Do not silently retry indefinitely, escalate models, or declare completion. Routine formatting fixes are not a substantial cycle; a further behaviour correction is.

## Completion

The active acceptance criteria, relevant verification, documentation impact, and review findings are accounted for. Report the delivered behaviour, remaining limitations, checks actually run, review outcome, and model evidence where delegation was used. Preserve the existing project's commit/PR conventions. Name the next issue without automatically starting it.
