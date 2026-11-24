# Agent Setup

Modular, token-conscious agent workflows and skills for coding and non-coding projects. Shared project methods, lean coding workflows, and cost-aware profiles for Codex, Claude Code, and ChatGPT.

## Current state

The foundation is documented. Implementation is tracked in the [prioritised roadmap](docs/roadmap.md). There is no installer, working profile switcher, or released skill bundle yet. The ACS workflow can already be read and applied as guidance; its runtime behaviour and savings still need a pilot.

This is a new, parallel repository. [coding-agent-setup](https://github.com/hubisan/coding-agent-setup) and [agent-project-setup](https://github.com/hubisan/agent-project-setup) remain intact as sources and working alternatives.

## Modules

| Part | Purpose | Initial scope |
| --- | --- | --- |
| Shared core | Installation, configuration, provider adapters, and evidence conventions | Planned implementation |
| APS | Reusable project methods for software and non-software work | [Boundaries and candidate catalogue](modules/aps/README.md) |
| ACS | Coding workflow and optional specialised methods; depends on APS | [Adaptive workflow](modules/acs/WORKFLOW.md) |
| GTD | Optional future module for reusable task practices | Reserved boundary only; no skills planned now |

Memento and its `mem-*` adapters remain in the Memento repository. Teaching and learning are outside this setup.

## Start here

- To pick work: [roadmap and dependencies](docs/roadmap.md).
- To understand agreed scope: [consolidated decisions](docs/decisions.md).
- To change module or installation boundaries: [architecture](docs/architecture.md).
- To configure models: [profile policy](docs/models.md). `balanced` is the default; Sol never exceeds `medium`.
- To propose a skill or add instructions: [design and evidence gate](docs/skill-design.md).
- To trace existing work and external ideas: [sources and adoption status](docs/sources.md).

Install only the needed modules and skills when installation is implemented. A workflow step does not require a corresponding skill. Plan, spec, tickets, implementation, tests, documentation, and review are used in proportion to the task, rather than as a compulsory sequence.
