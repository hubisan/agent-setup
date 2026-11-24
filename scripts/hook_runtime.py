#!/usr/bin/env python3
"""Small, local hook runtime. Never reads transcripts or makes network calls."""
import hashlib
import json
import os
from pathlib import Path
import signal
import re
import stat
import sys
import time
from datetime import datetime, timezone

PROVIDERS = ('codex', 'claude-code')
EFFORTS = ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max')
EVENTS = {
    'codex': {'SessionStart', 'SessionEnd', 'PreToolUse', 'SubagentStart',
              'SubagentStop', 'PreModelRequest', 'PostModelRequest'},
    'claude-code': {'SessionStart', 'SessionEnd', 'PreToolUse', 'SubagentStart',
                    'SubagentStop', 'PreModelSwitch', 'PostModelSwitch', 'ConfigChange'},
}
BLOCKING = {'PreToolUse', 'PreModelSwitch'}
MAX_INPUT = 2 * 1024 * 1024
MAX_DAY = 5 * 1024 * 1024
ASTRA = ('astra', 'gpt-6-astra', 'gpt-6.2-astra')
USAGE_FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens', 'output_tokens',
                'reasoning_output_tokens', 'total_tokens')


def identifier(value):
    # IDs are correlation keys, not free text. Never retain their raw values.
    if isinstance(value, str) and 0 < len(value) <= 256:
        return hashlib.sha256(value.encode()).hexdigest()
    return None


def observation(provider, payload, policy):
    """Extract only explicitly understood fields, with no inherited-value guesses."""
    event = payload.get('hook_event_name')
    if not isinstance(event, str) or event not in EVENTS[provider]:
        return None
    role = payload.get('agent_type')
    model, effort = None, None
    evidence = 'observed-event'
    if event == 'PreToolUse':
        tools = ('spawn_agent', 'Agent') if provider == 'codex' else ('Agent',)
        if payload.get('tool_name') not in tools:
            return None
        args = payload.get('tool_input')
        if not isinstance(args, dict):
            args = {}
        role = args.get('agent_type' if provider == 'codex' else 'subagent_type')
        model = args.get('model')
        effort = args.get('reasoning_effort' if provider == 'codex' else 'effort')
        evidence = 'requested'
    elif event in ('PreModelSwitch', 'PostModelSwitch'):
        model = payload.get('to_model')
        evidence = 'requested' if event == 'PreModelSwitch' else 'session-model-observed'
    elif event in ('PreModelRequest', 'PostModelRequest', 'SessionStart'):
        model = payload.get('model')
        evidence = 'request-model-observed' if event != 'SessionStart' else 'session-model-observed'
    elif event in ('SubagentStart', 'SubagentStop'):
        # The common model field is not proof of the child's effective routing.
        evidence = 'spawn-confirmed'
    if isinstance(role, str) and role.startswith('acs-'):
        role = role[4:]
    role = role if isinstance(role, str) and role in policy['plan']['roles'] else None
    return event, role, model, effort, evidence


def check(policy, role, model, effort, event=None):
    """Return a bounded reason code; unknown values never authorise or deny."""
    allowed = policy['allowed']
    expected = policy['plan']['roles'].get(role)
    if isinstance(model, str) and model in ASTRA:
        return 'violation', 'astra-prohibited'
    known_model = isinstance(model, str) and model in allowed
    # Claude documents to_model as a canonical ID, unlike unresolved Agent aliases.
    if (event == 'PreModelSwitch' and isinstance(model, str)
            and re.fullmatch(r'claude-[a-z0-9-]+', model) and not known_model):
        return 'violation', 'model-outside-policy'
    known_effort = isinstance(effort, str) and effort in EFFORTS
    if known_model and known_effort and effort not in allowed[model]:
        return 'violation', 'effort-prohibited'
    if expected and role != 'coordinator':
        if known_model and model != expected['model']:
            return 'violation', 'role-model-mismatch'
        if known_effort and effort != expected['effort']:
            # Do not substitute max/xhigh or infer an unseen model.
            return 'violation', 'role-effort-mismatch'
        if expected['approval_required']:
            return 'unknown', 'escalation-approval-unobserved'
    if not known_model or not known_effort:
        return 'unknown', 'model-or-effort-unobserved'
    if effort == 'xhigh' and not (expected and expected['effort'] == 'xhigh'
                                  and expected['requested_effort'] == 'max'
                                  and policy['plan']['capability_version']):
        return 'unknown', 'fallback-unverified'
    if policy['plan']['provider'] == 'claude-code' and model in allowed:
        if policy['plan']['profile'] != 'quality' and model == policy['plan']['roles']['implementer-escalated']['model']:
            return 'unknown', 'escalation-approval-unobserved'
    return 'within-observed-policy', 'observed-pair-only'


def usage(payload, event):
    raw = payload.get('token_usage') if event == 'PostModelRequest' else None
    if not isinstance(raw, dict):
        return None
    result = {key: raw[key] for key in USAGE_FIELDS
              if type(raw.get(key)) is int and raw[key] >= 0}
    return result or None


def safe_version(value):
    return value if isinstance(value, str) and re.fullmatch(r'v?\d+(?:\.\d+){1,3}|fixture', value) else None


def event_record(provider, payload, policy, obs, guard_enabled, started):
    event, role, model, effort, evidence = obs
    verdict, reason = check(policy, role, model, effort, event)
    known_models = set(policy['allowed']) | set(ASTRA) | {'sonnet', 'opus', 'inherit'}
    source = payload.get('source')
    sources = ('startup', 'resume', 'clear', 'compact', 'fork', 'command', 'picker',
               'sdk', 'auto', 'user_settings', 'project_settings', 'local_settings',
               'policy_settings', 'skills')
    status = payload.get('status') if event == 'PostModelRequest' else None
    return {
        'schema': 1, 'time_utc': datetime.now(timezone.utc).isoformat(),
        'provider': provider, 'client_version': None,
        'configured_capability_version': safe_version(policy['plan']['capability_version']),
        'event': event, 'source': source if source in sources else None,
        'session_id': identifier(payload.get('session_id')),
        'agent_id': identifier(payload.get('agent_id')),
        'turn_id': identifier(payload.get('turn_id')),
        'tool_use_id': identifier(payload.get('tool_use_id')),
        'role': role, 'model': model if isinstance(model, str) and model in known_models else None,
        'effort': effort if isinstance(effort, str) and effort in EFFORTS else None,
        'evidence': evidence, 'runtime_verified': False,
        'policy_result': verdict, 'policy_reason': reason,
        'guard_enabled': guard_enabled,
        'status': status if status in ('completed', 'failed', 'cancelled') else None,
        'usage': usage(payload, event), 'usage_scope': 'attempt' if event == 'PostModelRequest' else None,
        'model_duration_ms': None,
        'hook_processing_ms': round((time.monotonic() - started) * 1000, 3),
    }


def append_event(project, record):
    # Fixed location outside the installed project. Do not follow symlinks,
    # accept shared application directories or open pipes/devices.
    home = Path.home().absolute()
    base = home / '.local/state/agent-setup-hooks'
    if project == base or project in base.parents:
        raise OSError('Telemetry location inside project')
    for parent in reversed(base.parents):
        parent.mkdir(exist_ok=True)
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise OSError('Unsafe telemetry parent')
    folder = base / identifier(str(project))
    for path in (base, folder):
        path.mkdir(mode=0o700, exist_ok=True)
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise OSError('Telemetry directory is not private')
    path = folder / ('events-' + record['time_utc'][:10] + '.jsonl')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or info.st_uid != os.getuid() or info.st_mode & 0o077):
            raise OSError('Telemetry file is not private')
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        data = (json.dumps(record, separators=(',', ':')) + '\n').encode()
        if os.fstat(fd).st_size + len(data) > MAX_DAY:
            raise OSError('Telemetry daily limit reached')
        if os.write(fd, data) != len(data):
            raise OSError('Incomplete telemetry write')
    finally:
        os.close(fd)


def response(obs, policy):
    event, role, model, effort, evidence = obs
    verdict, reason = check(policy, role, model, effort, event)
    if verdict == 'violation' and event in BLOCKING:
        return {'hookSpecificOutput': {'hookEventName': event,
                                      'permissionDecision': 'deny',
                                      'permissionDecisionReason': 'Agent Setup: ' + reason}}
    if event == 'PreModelRequest' and verdict != 'violation':
        # Diagnostic-only hook: don't repeat an unknown-effort message on every attempt.
        return {}
    if verdict != 'within-observed-policy':
        return {'systemMessage': 'Agent Setup: ' + reason + '; effective routing not verified.'}
    return {}


def deadline(_signum, _frame):
    raise TimeoutError('Hook deadline')


def main():
    started = time.monotonic()
    # Stay below host timeout; never turn an internal error into exit 2.
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 0.75)
    try:
        provider, mode = sys.argv[1:]
        if provider not in PROVIDERS or mode not in ('guard', 'telemetry', 'both'):
            raise ValueError('Unsupported invocation')
        folder = Path(__file__).resolve().parent
        policy = json.loads((folder / ('policy-' + provider + '.json')).read_text())
        if policy['schema'] != 1 or policy['plan']['provider'] != provider:
            raise ValueError('Unknown policy')
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise ValueError('Oversized input')
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError('Unknown payload')
        obs = observation(provider, payload, policy)
        result = {}
        if obs:
            if mode in ('guard', 'both'):
                result = response(obs, policy)
            if mode in ('telemetry', 'both'):
                try:
                    append_event(folder.parents[1], event_record(
                        provider, payload, policy, obs, mode == 'both', started))
                except (OSError, ValueError, TypeError):
                    # Storage failure must not discard an already confirmed denial.
                    print('Agent Setup: telemetry unavailable', file=sys.stderr)
        else:
            print('Agent Setup: event not understood', file=sys.stderr)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        print('Agent Setup: hook evidence unavailable', file=sys.stderr)
        return 1
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    sys.exit(main())
