# Skill and instruction design gate

Apply this gate whenever creating or revising a skill, repository instruction, or workflow. It is a development reference, not context that every target task must load.

## Required design reference

The owner selected OpenAI's [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) as a design input. Its relevant guidance is to narrow descriptions to real triggers, disclose supporting material only when relevant, replace rigid recipes with useful guidance, and make repository reading conditional. Clear completion boundaries also matter. The article discusses Astra; validate the resulting instructions on our intended models instead of assuming the same effects for Luna, Terra, Sol, or Claude.

## Small contract

Describe the user problem, trigger and exclusions, necessary inputs, useful result, and completion boundary. Start with the smallest workflow or reference that can solve it. Create a skill only if packaging improves reuse or selection. A workflow phase or upstream skill name alone does not justify another skill.

Keep the description short enough to distinguish the trigger. Keep `SKILL.md` focused; link coding-specific or host-specific detail with explicit read conditions. Avoid duplicating core policy, instructions the agent already follows, or the same method across APS and ACS. Record the source, adopted ideas, changes, and required notices when deriving material.

## Acceptance evidence

| Question | Minimum useful evidence |
| --- | --- |
| Is it discoverable? | Package/metadata validation in the intended host. |
| Is it selected appropriately? | Fresh-context natural prompts, explicit invocation, and prompts where it should not activate. Record host traces when available; otherwise mark selection uncertain. |
| Does it behave correctly? | A small set of realistic success, boundary, and failure scenarios with observable results. |
| Does it add value? | Compare equivalent tasks with the lean workflow alone and with the candidate. Record quality, omissions, interruptions, and rework. |
| What does it cost? | Record available context/token/credit and elapsed-time observations, including delegates and retries; label unavailable data. |
| Is it accepted? | Independent review and explicit user acceptance for that candidate, with evidence links and remaining host limitations. |

Use a small repeatable pilot, not an elaborate evaluation platform. Do not infer a general win from one successful example. A skill's own claim that it ran is weaker than a host activation trace; successful manual use does not establish natural activation.

States are candidate, prototype, pilot, and accepted. A merged source PR, a valid package, or a previous UI pilot is not acceptance of a changed package on another host. Retest the changed behaviour rather than every historical scenario by default.

## Context cost to account for

Where a host exposes skill names and descriptions for discovery, even an unused installed skill can add metadata context. Invoking it loads instructions; references and tool outputs add more when read. Independent agent sessions also consume their own brief and relevant context. Exact loading, caching, and billing depend on the host and must be measured or marked unknown.

Consequently, selective installation, specific triggers, conditional references, short outputs, and sufficient downstream artifacts are part of the design. Do not strip useful Luna reasoning or necessary review merely to make one prompt smaller. Keep an addition only when its observed contribution justifies its total task cost.
