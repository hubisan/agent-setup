# Sources and adoption status

Checked 2026-11-24. The owner's consolidated decisions in [decisions.md](decisions.md) override conflicting historical proposals. Sources remain in their original repositories; no issue transfer, old-repository edit, or automatic upstream synchronisation is part of this bootstrap.

## Existing setups

| Source | Observed state and use |
| --- | --- |
| [coding-agent-setup at `074088a`](https://github.com/hubisan/coding-agent-setup/tree/074088ae0381f87ff1dae044145b1c5cce192f1a) | Working source for roles, downstream artifacts, model evidence, review/correction, documentation and installation experience. Replace mandatory delegation/skills and Sol `high`; evaluate the documented Luna compatibility fallback. |
| [agent-project-setup at `012e5cc`](https://github.com/hubisan/agent-project-setup/tree/012e5ccea945e8bb0872c426179fb41584340671) | Source for reusable APS methods, project ownership, selective context and pilot conventions. Historical decisions/scenarios remain there; do not load or copy them wholesale. |
| [APS roadmap #11](https://github.com/hubisan/agent-project-setup/issues/11) | Method catalogue and APS/Memento/GTD boundary. Some narrative status is stale; use actual PR state and current files. |
| [APS clarify #14](https://github.com/hubisan/agent-project-setup/issues/14), [PR #21](https://github.com/hubisan/agent-project-setup/pull/21) | PR merged on 2026-11-02. Current skill identifies itself as pilot v0.3.4, not a release or approval. Earlier inline-layout acceptance does not validate the later custom-input revision or current reported regressions. |
| [APS form UX #23](https://github.com/hubisan/agent-project-setup/issues/23) | Historical Copy/Submit/remarks requirements, extended by current dropped-character feedback. Test actual host behaviour, preserve useful fallbacks. |
| [APS handoff #20](https://github.com/hubisan/agent-project-setup/issues/20), [PR #22](https://github.com/hubisan/agent-project-setup/pull/22) | PR remains open and draft. Label correction to `handoff`, cross-agent pilot, and parallel handoff evidence remain work. |
| [APS documentation #24](https://github.com/hubisan/agent-project-setup/issues/24) | Candidate for human and agent documentation; includes comparison with `writing-for-agents`, project-layout preservation, and real pilot gates. |
| [APS review #19](https://github.com/hubisan/agent-project-setup/issues/19) | Source for actual progress, blockers, and next actions; retained as `aps-project-review` candidate here. |
| [APS questionnaire #25](https://github.com/hubisan/agent-project-setup/issues/25) | Separate stakeholder-questionnaire candidate; not conflated with live clarification. |
| [APS outcomes #8](https://github.com/hubisan/agent-project-setup/issues/8), [#9](https://github.com/hubisan/agent-project-setup/issues/9), [#10](https://github.com/hubisan/agent-project-setup/issues/10) | Historical Memento/GTD traceability only. Do not create corresponding APS/GTD implementation tickets here. |

## External inputs

- [OpenAI instruction-design article](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), published 2026-09-11: required design input, applied through the [design gate](skill-design.md). It does not prove savings or skill efficacy on this setup's models.
- [Matt Pocock's skills](https://github.com/mattpocock/skills): candidate methods and vocabulary, especially domain modelling, decision-oriented exploration, and handoff. Existing local variants may differ from upstream; inspect the precise revision before deriving a package.
- [Addy Osmani's skill catalogue](https://skills.addy.ie/skills/) and [source repository](https://github.com/addyosmani/agent-skills): selective comparison material for planning, debugging, review and documentation. No wholesale import or measured-benefit claim.

This bootstrap imports no upstream skill package. Before copying one, record the exact source revision and applicable licence/notices, then record intentional deviations. Keep future upstream updates reviewable; never silently overwrite a maintained variant. The source coding setup has an MIT licence; no root `LICENSE` was found in APS at the checked revision. This observation does not choose a licence for this repository.
