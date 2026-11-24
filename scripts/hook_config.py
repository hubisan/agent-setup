"""Build native command registrations and a snapshot of the existing profile policy."""
import profile as profiles

PATHS = {'codex': '.codex/hooks.json', 'claude-code': '.claude/settings.json'}


def policy_for(plan):
    return {'schema': 1, 'plan': plan,
            'allowed': {model: list(efforts)
                        for model, efforts in profiles.MODELS[plan['provider']].values()}}


def registrations(provider, guard, telemetry):
    """One handler per event, even when both features are selected."""
    guard_events = {'SessionStart', 'PreToolUse'}
    telemetry_events = {'SessionStart', 'SessionEnd', 'PreToolUse', 'SubagentStart', 'SubagentStop'}
    if provider == 'codex':
        guard_events |= {'PreModelRequest'}
        telemetry_events |= {'PreModelRequest', 'PostModelRequest'}
        command = 'root=$(git rev-parse --show-toplevel) || exit 1; exec python3 "$root/.agents/hooks/runtime.py"'
        matcher = '^(spawn_agent|Agent)$'
    else:
        guard_events |= {'PreModelSwitch', 'PostModelSwitch'}
        # A PreModelSwitch timeout can cancel a switch. Do not add that
        # boundary solely for observation; PostModelSwitch records changes.
        telemetry_events |= {'PostModelSwitch', 'ConfigChange'}
        command = 'exec python3 "$CLAUDE_PROJECT_DIR/.agents/hooks/runtime.py"'
        matcher = '^Agent$'
    result = {}
    for event in sorted((guard_events if guard else set()) | (telemetry_events if telemetry else set())):
        g, t = guard and event in guard_events, telemetry and event in telemetry_events
        if provider == 'claude-code' and event == 'PreModelSwitch' and telemetry:
            t = True
        mode = 'both' if g and t else 'guard' if g else 'telemetry'
        group = {'hooks': [{'type': 'command', 'command': f'{command} {provider} {mode}', 'timeout': 2}]}
        if event == 'PreToolUse':
            group['matcher'] = matcher
        result[event] = [group]
    return result
