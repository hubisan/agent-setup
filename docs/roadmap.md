# Prioritised roadmap

The live execution index is [#1](https://github.com/hubisan/agent-setup/issues/1). GitHub issues own scope, acceptance criteria, dependencies, and current status. This file is the navigation map, not a second ticket tracker.

Foundation complete: repository boundaries, decisions, adaptive ACS contract, profile policy, candidate catalogue, design gate, and source traceability. Profile planning, rendering and supplied-configuration audit are implemented with local tests (#2); actual target-client checks remain open. The evaluation protocol and a local configuration example exist (#4). The selective installer and adoption guide are implemented in #3; independent review, host verification and the release licence gate remain open. Packaged skills and live runtime evidence remain open.

## Delivery order

| Priority | Issue | Outcome | Depends on |
| --- | --- | --- | --- |
| P0 | [#2](https://github.com/hubisan/agent-setup/issues/2) | Validated profile schema and Codex/Claude Code adapters | Foundation |
| P0 | [#3](https://github.com/hubisan/agent-setup/issues/3) | Selective, repeatable installation and safe updates | Profiles |
| P0 | [#4](https://github.com/hubisan/agent-setup/issues/4) | Small repeatable evaluation protocol and evidence records | Foundation; can run alongside profile work |
| P0 | [#5](https://github.com/hubisan/agent-setup/issues/5) | First usable ACS slice, exercised in both coding hosts | Profiles, installer, evidence protocol |
| P1 | [#6](https://github.com/hubisan/agent-setup/issues/6) | Supported selective ChatGPT package/install/update path | Installer, evidence protocol |
| P1 | [#7](https://github.com/hubisan/agent-setup/issues/7) | Adapted clarify pilot with real form regression checks | ACS pilot and ChatGPT path |
| P1 | [#8](https://github.com/hubisan/agent-setup/issues/8) | One evaluated APS documentation candidate | ACS pilot and evidence protocol |
| P1 | [#9](https://github.com/hubisan/agent-setup/issues/9) | Verified cross-agent and parallel handoff candidate | ACS pilot, ChatGPT path, evidence protocol |
| P1 | [#10](https://github.com/hubisan/agent-setup/issues/10) | General domain modelling with conditional coding detail | ACS pilot and evidence protocol |
| P1 | [#11](https://github.com/hubisan/agent-setup/issues/11) | Evidence-based project status review candidate | ACS pilot and evidence protocol |
| P2 | [#12](https://github.com/hubisan/agent-setup/issues/12) | Reassess APS/ACS catalogue; retain, simplify, replace, defer or drop methods | ACS pilot and evidence protocol |

P0 delivers the lean coding setup before the skill catalogue expands. P1 skills are developed and accepted individually; their listing is not a bulk implementation instruction. Preparation can overlap where dependencies permit, but do not release a candidate before its own gates pass.

Complete the outstanding profile verification and review gates before using the generated files in an installed target. The evaluation protocol is available for the pilot. Do not make the first ACS slice depend on completion of optional APS skills. Use the existing [workflow](../modules/acs/WORKFLOW.md) and shared APS contract.

GTD implementation, Memento features, teaching, migration of old repositories, and automatic import of upstream bundles are outside this roadmap. Remaining APS names stay in the [catalogue](../modules/aps/README.md) until a concrete need justifies an issue. #12 records a catalogue-wide reassessment after the pilot; individual candidate gates apply before implementation and do not depend on completing #12.
