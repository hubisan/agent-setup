# Consolidated decisions

Baseline: 2026-11-24. Source: the owner's setup discussion, its clarification answers, and the instruction to initialise this repository and create the roadmap. This is a consolidated record, not a transcript or a claim that planned features are implemented.

## Confirmed direction

| ID | Decision | Consequence |
| --- | --- | --- |
| D01 | Create `hubisan/agent-setup` as a parallel monorepo. | Do not rename, merge, archive, or automatically migrate the existing repositories. |
| D02 | Separate shared core, APS, and ACS; ACS requires APS. | Share general methods without copying them into coding skills. Install only the required APS subset. |
| D03 | Reserve an optional GTD module, but create no GTD skills now. | No invented `gtd-clarify` or task-system backlog. Memento-specific storage and `mem-*` stay in Memento. |
| D04 | Use namespaced skills: `aps-*`, `acs-*`, and future `gtd-*`. | Avoid clashes with upstream or provider skills. `as-*` is superseded. |
| D05 | Support Codex, Claude Code, and ChatGPT. | Implement Codex and Claude Code profiles together; treat ChatGPT distribution and model control separately. |
| D06 | Offer `economy`, default `balanced`, and `quality`. | Apply the [model policy](models.md); Sol is capped at `medium`, including escalation. Preserve Luna's existing effort choices. |
| D07 | Start with a lean ACS workflow and profiles. | Do not build the whole skill catalogue before the first usable coding setup. |
| D08 | Use simple, normal, and complex work paths, with risk before size. | Reuse existing plans/specs/tickets; create missing artifacts only when useful. |
| D09 | Use adaptive delegation and testing. | Delegate for cheaper suitable execution, independent review, or useful parallel work; account for added context. TDD is conditional. |
| D10 | Independently review normal/complex behaviour changes. | Preserve the existing one-substantial-correction budget and explicit unresolved-failure boundary. |
| D11 | Check documentation impact on every task. | Update affected documentation in the change, or state why none is needed. |
| D12 | Make `aps-writing-docs` a shared APS/core capability. | One candidate with conditional human/agent references. Replacing `writing-for-agents` requires comparison, not assumption. |
| D13 | Keep `aps-analyze` and `aps-domain-modeling` distinct. | Broad situation/requirements analysis differs from precise domain vocabulary, relationships, and rules. One domain skill has an optional coding reference. |
| D14 | Use `aps-solution-design`. | It compares ways to solve a problem; it does not imply visual design. Preserve project-status review as a separate APS capability. |
| D15 | Prefer a workflow to an automatic coding-skill chain. | No compulsory Plan > Spec > Tickets > Implement > Test > Review sequence and no mandatory TDD skill. |
| D16 | Install selectively and evolve our own variants. | Review upstream changes deliberately; retain provenance and applicable notices for reused material. |
| D17 | Test and accept each skill individually. | Separate discovery/activation, behaviour, incremental benefit, and cost. Manual invocation cannot prove automatic selection. |
| D18 | Apply the OpenAI instruction-design reference to every new or revised skill. | Keep task-specific guidance short and conditional, and test with the intended models. See [design gate](skill-design.md). |
| D19 | Use Matt Pocock and Addy Osmani as selective inputs. | Borrow a method only for a concrete gap; no wholesale bundle or unmeasured benefit claim. |
| D20 | Exclude a teaching/learning module. | The separate learning platform owns that work; no general `teach` skill or broad writing module is added here. |

Answer provenance: Q1–4 establish module/dependency/domain boundaries; Q5 explicitly excludes GTD skills now; Q6–10 establish selective installation, own evolution, individual validation, a new parallel repository, and three hosts; Q11–15 establish workflow-first coding, adaptive delegation, selective inspiration, both coding providers, and ACS/profile priority. Q16–20 were accepted through “übernehme deine Empfehlungen”: automatic classification, independent review, documentation on every task, one documentation skill, and adaptive tests. The question texts are not reconstructed from their answer letters alone.

## Clarification-form feedback to retain

Recommendations should be visibly marked and preselected where supported. Preselection is not consent; only an explicit answer or submission confirms a choice. Preserve stable question numbers, custom answers, and a separate remarks field. Copy and Submit must be available and distinct. Copy must not submit. Investigate dropped characters during rapid typing, focus stability, and input composition in the actual host.

The existing clarify skill's latest layout uses a bold title and normal explanation in one flowing radio-option block. Host limitations need a usable fallback, not a promise that prompt text alone controls the UI. The previous inline-layout pilot and later regressions have different evidence states; see [source status](sources.md).

## Bootstrap implementation choices

The following are agent-selected, reversible organisation choices, not additional user decisions:

- Keep English documentation, inherited from both source setups; use one short entry point and conditional references.
- Use `modules/aps` and `modules/acs` for method sources. Keep provider adapters, profile data, and installation code separate when implemented.
- Use `aps-project-review` as the clearer canonical name for the requested `aps-review` capability; record the old name in the catalogue. `aps-wayfinder` remains a candidate name for decision-oriented exploration.
- Keep GitHub issues authoritative for execution scope and dependencies; the repository roadmap is a compact navigation index.
- Record the GTD boundary in architecture rather than create empty modules or speculative tickets.

## Decisions deferred until relevant evidence exists

Initial provider model IDs and role mappings, including the inventory-driven Luna fallback, are now implemented as agent-selected proposals in the profile catalogue. Client-specific availability and override resolution still require verification. Do not infer them from profile names. Real savings, automatic skill activation, a replacement for `writing-for-agents`, and promotion of any optional coding skill remain unproven. Select the repository's distribution licence before the first packaged release; no licence is inferred from a public repository or from another project's licence.

These decisions supersede the old mandatory skill chain, unconditional delegation, and Sol `high` escalation. They do not discard unrelated source-project requirements or turn the old APS historical audit into mandatory context.

### Claude profile refinement (2026-11-24)

User-approved adjustment before merging PR #13: use Sonnet for regular work in economy and balanced, including Sonnet high for balanced review and complex implementation. Reserve Opus low for approved escalation in these profiles. Quality retains Opus medium for demanding roles and recommends Sonnet medium as coordinator. Use Sonnet 5.5 and Opus 5.5, subject to target-client availability. Codex mappings are unchanged. The revised mappings are starting configurations, not measured savings or validated runtime behaviour.
