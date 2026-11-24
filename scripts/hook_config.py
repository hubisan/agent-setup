"""Build native command registrations and a snapshot of the existing profile policy."""
import json
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


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(data):
    """Reject duplicate keys and non-JSON constants before modifying settings."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate key in hook settings')
            result[key] = value
        return result

    def bad_constant(_value):
        raise ValueError('Invalid JSON constant in hook settings')

    return json.loads(data, object_pairs_hook=object_pairs, parse_constant=bad_constant)


def settings_document(data):
    document = strict_json(data) if data is not None else {}
    require(isinstance(document, dict), 'Hook settings must be a JSON object')
    events = document.get('hooks', {})
    require(isinstance(events, dict), 'Unsupported hooks settings shape')
    for groups in events.values():
        require(isinstance(groups, list) and all(
            isinstance(group, dict) and isinstance(group.get('hooks'), list)
            and all(isinstance(handler, dict) for handler in group['hooks'])
            for group in groups), 'Unsupported hook event group')
    return document


def references_runtime(value):
    if isinstance(value, dict):
        return any(references_runtime(v) for v in value.values())
    if isinstance(value, list):
        return any(references_runtime(v) for v in value)
    return isinstance(value, str) and '.agents/hooks/runtime.py' in value


def validate_record(path, row):
    provider = next((name for name, value in PATHS.items() if value == path), None)
    require(provider is not None and row['kind'] == 'hooks'
            and set(row) == {'kind', 'groups', 'created_file', 'created_hooks', 'created_events'},
            'Invalid hook ownership record')
    require(type(row['created_file']) is bool and type(row['created_hooks']) is bool
            and isinstance(row['groups'], dict) and row['groups']
            and isinstance(row['created_events'], list)
            and all(isinstance(event, str) and event in row['groups'] for event in row['created_events'])
            and len(set(row['created_events'])) == len(row['created_events']),
            'Invalid hook ownership record')
    for groups in row['groups'].values():
        require(isinstance(groups, list) and len(groups) == 1 and isinstance(groups[0], dict)
                and isinstance(groups[0].get('hooks'), list) and len(groups[0]['hooks']) == 1,
                'Invalid owned hook group')
        handler = groups[0]['hooks'][0]
        require(isinstance(handler, dict) and handler.get('type') == 'command'
                and isinstance(handler.get('command'), str)
                and '.agents/hooks/runtime.py' in handler['command']
                and handler['command'].split()[-2:] in (
                    [provider, 'guard'], [provider, 'telemetry'], [provider, 'both']),
                'Invalid owned hook handler')


def merge_settings(path, data, old, desired):
    """Own exact hook groups, never the settings document or other handlers."""
    doc = settings_document(data)
    events = doc.get('hooks', {})
    previous = old['groups'] if old else {}
    if old:
        validate_record(path, old)
        require(data is not None, f'Edited or missing managed hooks: {path}')
    for event, groups in previous.items():
        require(event in events and events[event].count(groups[0]) == 1,
                f'Edited, missing or duplicate managed hook group: {path}/{event}')
    for event, groups in events.items():
        for group in groups:
            if event in previous and group == previous[event][0]:
                continue
            require(not references_runtime(group),
                    f'Unowned Agent Setup hook registration: {path}/{event}')
    if desired == previous:
        return data, old

    created_file = old['created_file'] if old else data is None
    created_hooks = old['created_hooks'] if old else 'hooks' not in doc
    created_events = set(old['created_events'] if old else [])
    for event in sorted(set(previous) | set(desired)):
        before = previous.get(event)
        after = desired.get(event)
        if before:
            index = events[event].index(before[0])
            if after:
                events[event][index] = after[0]
            else:
                del events[event][index]
                if event in created_events and not events[event]:
                    del events[event]
                created_events.discard(event)
        elif after:
            if event not in events:
                created_events.add(event)
                events[event] = []
            events[event].append(after[0])

    if events or not created_hooks:
        doc['hooks'] = events
    else:
        doc.pop('hooks', None)
    if not desired and created_file and not doc:
        return None, None
    # Preserve semantic values and order; normalise JSON formatting only on change.
    result = (json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
    record = {'kind': 'hooks', 'groups': desired, 'created_file': created_file,
              'created_hooks': created_hooks, 'created_events': sorted(created_events)}
    return result, record if desired else None
