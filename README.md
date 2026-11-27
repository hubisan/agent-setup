# Agent Setup

Modular, token-conscious agent workflows and skills for coding and non-coding projects. Shared project methods, lean coding workflows, and cost-aware profiles for Codex, Claude Code, and ChatGPT.

## Current state

The foundation is documented. Implementation is tracked in the [prioritised roadmap](docs/roadmap.md). Profile planning, native agent-file generation and a configuration audit are available for Codex and Claude Code. See [profile commands](docs/models.md#profile-commands). The [evaluation protocol](docs/evaluation/README.md) is available for pilots. The project-local [installer and adoption guide](docs/adoption.md) support selective APS/ACS installation, updates and removal. Optional [model-routing guard and local telemetry](docs/hooks.md) are implemented and off by default. The [ACS pilot](docs/evaluation/pilot/README.md) defines reproducible live comparisons. There is no released skill bundle; live host compatibility, runtime behaviour and savings still need verification.

This is a new, parallel repository. [coding-agent-setup](https://github.com/hubisan/coding-agent-setup) and [agent-project-setup](https://github.com/hubisan/agent-project-setup) remain intact as sources and working alternatives.

## Modules

| Part | Purpose | Initial scope |
| --- | --- | --- |
| Shared core | Installation, configuration, provider adapters, and evidence conventions | Profile tooling, installer and evidence protocol |
| APS | Reusable project methods for software and non-software work | [Boundaries and candidate catalogue](modules/aps/README.md) |
| ACS | Coding workflow and optional specialised methods; depends on APS | [Adaptive workflow](modules/acs/WORKFLOW.md) and [candidate catalogue](modules/acs/README.md) |
| GTD | Optional future module for reusable task practices | Reserved boundary only; no skills planned now |

Memento and its `mem-*` adapters remain in the Memento repository. Teaching and learning are outside this setup.

## Start here

- To pick work: [roadmap and dependencies](docs/roadmap.md).
- To understand agreed scope: [consolidated decisions](docs/decisions.md).
- To adopt, update or remove the setup: [adoption guide](docs/adoption.md).
- To change module or installation boundaries: [architecture](docs/architecture.md).
- To configure models: [profile policy](docs/models.md). `balanced` is the default; Sol never exceeds `medium`.
- To propose a skill or add instructions: [design and evidence gate](docs/skill-design.md).
- To trace existing work and external ideas: [sources and adoption status](docs/sources.md).

Run the checks with `python3 -m unittest discover -s tests -v` (Python 3.11+, standard library only). Install only the needed modules and accepted skills. A workflow step does not require a corresponding skill. Plan, spec, tickets, implementation, tests, documentation, and review are used in proportion to the task, rather than as a compulsory sequence.
