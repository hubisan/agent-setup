# APS scope and candidate catalogue

APS supplies reusable project methods for coding and non-coding projects. The owner selected twelve candidates. Each candidate must pass the [design gate](../../docs/skill-design.md) before acceptance. [#12](https://github.com/hubisan/agent-setup/issues/12) owns remaining decisions and evidence. No candidate is an approved installation by default.

## APS target catalogue (owner direction)

| Candidate | Boundary |
| --- | --- |
| `aps-frame` | Define the purpose, desired outcome and scope without assuming a solution. |
| `aps-analyze` | Understand the current situation, stakeholders, causes, constraints, needs and requirements. |
| `aps-clarify` | Resolve material uncertainty and decisions that require the owner. [#7](https://github.com/hubisan/agent-setup/issues/7) |
| `aps-domain-modeling` | Define domain concepts, relationships and rules. Use examples and counterexamples. [#10](https://github.com/hubisan/agent-setup/issues/10) |
| `aps-solution-design` | Compare possible solutions and their trade-offs, including non-software solutions. |
| `aps-plan` | Organise concrete next actions and dependencies. |
| `aps-validate` | Verify outcomes against agreed requirements and evidence. |
| `aps-improve` | Improve an existing solution or working method based on observations. |
| `aps-writing-docs` | Use Simple English for people and Writing for Agents for AI. Keep documents concise and understandable. [#8](https://github.com/hubisan/agent-setup/issues/8) |
| `aps-project-review` | Assess actual progress, blockers and next actions. [#11](https://github.com/hubisan/agent-setup/issues/11) |
| `aps-handoff` | Transfer execution state and verify successful takeover. [#9](https://github.com/hubisan/agent-setup/issues/9) |
| `aps-wayfinder` | Explore a large uncertain goal across sessions with a map of decisions. |

## Integrated methods and exclusions

- Research and brainstorming are methods within framing, situation analysis and solution design, not separate skills.
- Stakeholder questionnaires belong to `aps-analyze`.
- Adoption uses the [installer and on-demand guide](../../docs/adoption.md), not `aps-adopt`. See [#3](https://github.com/hubisan/agent-setup/issues/3) and the [original adoption scenarios](https://github.com/hubisan/agent-project-setup/issues/12).
- No GTD, Memento or teaching skills in the current delivery. [#26](https://github.com/hubisan/agent-setup/issues/26) preserves future GTD compatibility.

## Domain modelling depth

Analysis asks what is happening and what is needed. Domain modelling asks what the concepts mean, how they relate, and which rules hold. Probe ambiguous terms with examples and counterexamples; capture resolved terminology promptly in the project's existing glossary or equivalent source.

For software, load a coding reference to compare the agreed model with actual code. Record contradictions and distinguish intended domain behaviour from current implementation; do not silently redefine the domain to match a bug. Preserve useful Matt Pocock conventions: concise glossary entries, scoped contexts and a navigation map only when helpful, and ADRs for consequential trade-offs. Keep feature requirements and implementation detail out of the glossary. Respect established Org/Markdown layout rather than impose a new one.

## Related catalogue

Use the [ACS catalogue](../acs/README.md) for coding-specific methods. Reuse shared APS methods rather than duplicate them under ACS.
