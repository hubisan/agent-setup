# APS scope and candidate catalogue

APS supplies reusable project methods for software and non-software work. These names define method boundaries, not installed or accepted skills. Recurring use and incremental value are prerequisites for packaging; the [design gate](../../docs/skill-design.md) applies to every candidate. The first delivery prioritises ACS workflow and profiles; accept APS candidates individually through the [design gate](../../docs/skill-design.md).

## Initial candidates

| Candidate | Responsibility | Source / next work |
| --- | --- | --- |
| `aps-clarify` | Resolve relevant uncertainty; reuse, verify, or decide routine choices before asking user-owned questions | Existing merged pilot v0.3.4; new-host behaviour and form regressions need testing. [#7](https://github.com/hubisan/agent-setup/issues/7) |
| `aps-writing-docs` | Maintain concise, navigable documentation for people and agents | Shared APS/core capability. Compare with `writing-for-agents`; no replacement decided. [#8](https://github.com/hubisan/agent-setup/issues/8) |
| `aps-handoff` | Transfer execution state and verify takeover, distinct from a decision summary | Existing draft; preserve authoritative ticket/spec and exact handoff identity. [#9](https://github.com/hubisan/agent-setup/issues/9) |
| `aps-domain-modeling` | Sharpen terms, relationships, rules, examples, and counterexamples | One skill with a conditional coding reference. [#10](https://github.com/hubisan/agent-setup/issues/10) |
| `aps-project-review` | Check actual project status, open work, blockers, and next actions | Requested as `aps-review`; clearer working name selected during bootstrap. [#11](https://github.com/hubisan/agent-setup/issues/11) |

## Reserved general methods

| Candidate | Boundary |
| --- | --- |
| `aps-frame` | Define purpose and desired outcome without assuming an app is needed. |
| `aps-analyze` | Understand the situation, stakeholders, problems, and requirements. |
| `aps-solution-design` | Compare approaches and trade-offs for solving the problem; supersedes `aps-design`. |
| `aps-plan` | Organise concrete next actions and dependencies. |
| `aps-validate` | Check outcomes against requirements and evidence. |
| `aps-improve` | Improve working methods based on observations; distinct from status review. |
| `aps-research` | Gather evidence and state uncertainty for a concrete question. |
| `aps-brainstorm` | Generate alternatives when variety is useful. |
| `aps-questionnaire` | Prepare targeted questions for another stakeholder; distinct from interviewing the current user. |
| `aps-wayfinder` | Explore an uncertain, large goal across sessions using a map of decisions; distinct from a delivery roadmap. |

Reserved methods are not an instruction to create all these skills. Start one only when the design gate justifies it.

## Initial packaging assessment

These are provisional design hypotheses, not measured usage or acceptance decisions. Revisit each in its actual use case before building a package.

| Methods | First form to evaluate |
| --- | --- |
| Clarify, writing-docs, handoff, domain-modeling, project-review | Existing candidate issues: test recurring use and additional value against native behaviour or a short reference. |
| Frame, analyze, solution-design, plan, validate, brainstorm | Native model capabilities and the shared workflow first. Package only a demonstrated recurring gap. |
| Improve, research | Native capabilities or targeted reference first; test whether a recurring project-specific method needs more. |
| Questionnaire, wayfinder | On-demand template or guide first; do not package solely because the method is reusable. |

## Adoption is not a skill

The owner rejected `aps-adopt` as a skill because project adoption is infrequent. [Installer #3](https://github.com/hubisan/agent-setup/issues/3) owns deterministic installation, updates and verification plus an on-demand adoption guide for existing project instructions and conflicts. Preserve the original [APS adoption scenarios](https://github.com/hubisan/agent-project-setup/issues/12). Do not add `aps-adopt` to discovery or duplicate the installer in agent instructions.

## Domain modelling depth

Analysis asks what is happening and what is needed. Domain modelling asks what the concepts mean, how they relate, and which rules hold. Probe ambiguous terms with examples and counterexamples; capture resolved terminology promptly in the project's existing glossary or equivalent source.

For software, load a coding reference to compare the agreed model with actual code. Record contradictions and distinguish intended domain behaviour from current implementation; do not silently redefine the domain to match a bug. Preserve useful Matt Pocock conventions: concise glossary entries, scoped contexts and a navigation map only when helpful, and ADRs for consequential trade-offs. Keep feature requirements and implementation detail out of the glossary. Respect established Org/Markdown layout rather than impose a new one.

## ACS candidates and exclusions

Bug/PR triage belongs to `acs-triage`, not `aps-triage`. Spec/ticket conversion, debugging, TDD, code review, architecture, prototypes, implementation, and merge-conflict help are possible ACS methods. They are not an approved install list: first test native capabilities and the lean workflow, then promote only a demonstrated recurring gap through [#12](https://github.com/hubisan/agent-setup/issues/12).

No `teach` module, broad `write` skill, Memento implementation, or GTD skills are included. Storage adapters must not recreate shared methods under another prefix.
