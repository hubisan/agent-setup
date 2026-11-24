#!/usr/bin/env python3
"""Preview, apply, inspect and recover a selective Agent Setup installation."""
import argparse
import base64
from contextlib import contextmanager
from dataclasses import dataclass
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile

import profile as profiles

ROOT = Path(__file__).resolve().parents[1]
STATE = '.agent-setup/state.json'
PENDING = '.agent-setup/pending.json'
START = b'<!-- agent-setup:begin -->'
END = b'<!-- agent-setup:end -->'
HOSTS = ('codex', 'claude-code')
SKILL_DIR = {'codex': '.agents/skills', 'claude-code': '.claude/skills'}
INSTRUCTIONS = ('AGENTS.md', 'CLAUDE.md')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    p = PurePosixPath(path)
    require(not p.is_absolute() and p.parts and p.as_posix() == path
            and all(x not in ('.', '..', '.git') for x in p.parts),
            f'Unsafe relative path: {path}')
    return p.parts


def owned_path(path):
    parts = relative(path)
    permitted = (path in INSTRUCTIONS or path == STATE
                 or path in ('.agent-setup/WORKFLOW.md', '.agent-setup/models.md',
                             '.agent-setup/profile-codex.json', '.agent-setup/profile-claude-code.json')
                 or re.fullmatch(r'\.codex/agents/acs-[a-z0-9-]+\.toml', path)
                 or re.fullmatch(r'\.claude/agents/acs-[a-z0-9-]+\.md', path)
                 or (len(parts) >= 4 and parts[:2] in (('.agents', 'skills'), ('.claude', 'skills'))
                     and re.fullmatch(r'(aps|acs)-[a-z0-9-]+', parts[2])))
    require(permitted, f'Path outside installer ownership: {path}')
    return path


def safe_path(root, rel, directory=False):
    """Check existing components without following any symlink."""
    parts = relative(rel)
    p = root
    for i, part in enumerate(parts):
        p = p / part
        try:
            info = p.lstat()
        except FileNotFoundError:
            continue
        expect_dir = i < len(parts) - 1 or directory
        require(not stat.S_ISLNK(info.st_mode), f'Symlink collision: {p}; preserve it and resolve manually')
        require(stat.S_ISDIR(info.st_mode) if expect_dir else stat.S_ISREG(info.st_mode),
                f'Unexpected path type: {p}')
        if not expect_dir:
            require(info.st_nlink == 1, f'Hard-link collision: {p}')
    return p


@dataclass(frozen=True)
class Snapshot:
    data: bytes
    mode: int = 0o644

    def fingerprint(self):
        return {'sha256': digest(self.data), 'mode': self.mode}

    def pack(self):
        return {'data': base64.b64encode(self.data).decode(), 'mode': self.mode}

    @classmethod
    def unpack(cls, row):
        if row is None:
            return None
        require(type(row['mode']) is int and 0 <= row['mode'] <= 0o777, 'Invalid journal mode')
        return cls(base64.b64decode(row['data'], validate=True), row['mode'])


def snapshot(root, rel):
    p = safe_path(root, rel)
    try:
        mode = stat.S_IMODE(p.stat().st_mode)
        require(mode <= 0o777, f'Special permission bits: {p}')
        return Snapshot(p.read_bytes(), mode)
    except FileNotFoundError:
        return None


def fingerprint(value):
    return value.fingerprint() if value is not None else None


def pack(value):
    return value.pack() if value is not None else None


def read_json(root, rel):
    value = snapshot(root, rel)
    return json.loads(value.data) if value is not None else None


def target_root(raw):
    root = Path(os.path.abspath(raw))
    for p in reversed((root, *root.parents)):
        info = p.lstat()
        require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode),
                f'Target requires real directories, not symlinks: {p}')
    require(root != ROOT and root not in ROOT.parents and ROOT not in root.parents,
            'Target must be separate from the source checkout')
    require(root != Path.home() and root != Path('/'), 'Choose a project directory, not a home or root directory')
    return root


@contextmanager
def target_lock(root):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def load_state(root):
    state = read_json(root, STATE)
    if state is None:
        require(snapshot(root, STATE) is None, 'Invalid null state; recover or inspect it manually')
        return None
    require(state['schema'] == 1 and isinstance(state['files'], dict), 'Unsupported installation state')
    for path, row in state['files'].items():
        owned_path(path)
        require(path != STATE and row['kind'] in ('file', 'block'), f'Invalid ownership: {path}')
        require((row['kind'] == 'block') == (path in INSTRUCTIONS), f'Invalid instruction ownership: {path}')
        if row['kind'] == 'file':
            require(re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
                    and type(row['mode']) is int and 0 <= row['mode'] <= 0o777, f'Invalid file record: {path}')
        else:
            text = row['text'].encode()
            require(text.count(START) == text.count(END) == 1 and text.endswith(END + b'\n')
                    and text.startswith((START, b'\n\n' + START)) and type(row['created']) is bool,
                    f'Invalid instruction block record: {path}')
    return state


def csv(value, default, allow_none=False):
    if value is None:
        return sorted(default)
    if value == 'none' and allow_none:
        return []
    values = value.split(',')
    require(all(values) and len(values) == len(set(values)), f'Invalid selection: {value}')
    return sorted(values)


def closure(names, entries, dependencies, label):
    found, visiting = set(), set()

    def visit(name):
        require(name in entries, f'Unknown or unavailable {label}: {name}')
        require(name not in visiting, f'Cyclic {label} dependency: {name}')
        if name in found:
            return
        visiting.add(name)
        for dep in dependencies(entries[name]):
            visit(dep)
        visiting.remove(name)
        found.add(name)

    for name in names:
        visit(name)
    return sorted(found)


def select(args, previous, manifest):
    old = previous['requested'] if previous else {}
    modules = csv(args.modules, old.get('modules', ['aps']))
    hosts = csv(args.providers, old.get('providers', HOSTS))
    skills = csv(args.skills, old.get('skills', []), allow_none=True)
    require(modules and hosts and set(hosts) <= set(HOSTS), 'Select modules and supported providers')
    accepted = {name: row for name, row in manifest['skills'].items()
                if row.get('status') == 'accepted'}
    selected_skills = closure(skills, accepted, lambda row: row.get('requires', []), 'accepted skill')
    needed = list(modules)
    for name in selected_skills:
        row = accepted[name]
        require(re.fullmatch(r'(aps|acs)-[a-z0-9-]+', name)
                and name.startswith(row['module'] + '-'), f'Invalid skill identity: {name}')
        needed.append(row['module'])
    selected_modules = closure(needed, manifest['modules'], lambda row: row['requires'], 'module')
    require(set(selected_modules) <= {'aps', 'acs'}, 'Module not implemented')
    profile = args.profile or old.get('profile') or 'balanced'
    capabilities = {}
    for host, value in [('codex', args.codex_capabilities), ('claude-code', args.claude_capabilities)]:
        if host not in hosts or 'acs' not in selected_modules:
            require(value is None, f'{host} capability input requires selected ACS host')
            continue
        cap = old.get('capabilities', {}).get(host) if value is None else (
            None if value == 'none' else profiles.read_json(value))
        if cap is not None:
            require(isinstance(cap, dict) and set(cap) == {'provider', 'version', 'models'},
                    'Capability inventory must contain only provider, version and models')
            require(isinstance(cap['models'], dict) and all(
                isinstance(name, str) and isinstance(efforts, list)
                and all(isinstance(effort, str) for effort in efforts)
                for name, efforts in cap['models'].items()), 'Invalid capability inventory model list')
            capabilities[host] = cap
    require('acs' in selected_modules or args.profile is None, 'Profile selection requires ACS')
    requested = {'modules': modules, 'providers': hosts, 'skills': skills,
                 'profile': profile if 'acs' in selected_modules else None,
                 'capabilities': capabilities}
    effective = {'modules': selected_modules, 'providers': hosts, 'skills': selected_skills,
                 'added_modules': sorted(set(selected_modules) - set(modules)),
                 'added_skills': sorted(set(selected_skills) - set(skills))}
    return requested, effective, accepted


def package_files(root, prefix):
    directory = safe_path(root, prefix, directory=True)
    require(directory.is_dir(), f'Missing skill package: {directory}')
    files = {}
    # Never recurse through symlink directories. Inspect each entry before reading.
    def walk_error(error):
        raise error

    for current, dirs, names in os.walk(directory, followlinks=False, onerror=walk_error):
        for name in dirs:
            safe_path(root, (Path(current) / name).relative_to(root).as_posix(), directory=True)
        for name in names:
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            data = snapshot(root, rel)
            require(data is not None, f'Package file disappeared: {path}')
            files[path.relative_to(directory).as_posix()] = data
    return files


def desired_files(requested, effective, accepted):
    files = {}
    blocks = {'AGENTS.md': (ROOT / 'core/APS.md').read_bytes()}
    if 'claude-code' in effective['providers']:
        blocks['CLAUDE.md'] = b'@AGENTS.md\n'
    if 'acs' in effective['modules']:
        blocks['AGENTS.md'] += (b'\nFor coding work, read [.agent-setup/WORKFLOW.md](.agent-setup/WORKFLOW.md) '
                                b'and follow its adaptive scope and review rules.\n')
        workflow = (ROOT / 'modules/acs/WORKFLOW.md').read_text()
        workflow = workflow.replace('../../docs/models.md#profile-commands', 'models.md')
        workflow = workflow.replace('../../docs/models.md', 'models.md')
        policy = (ROOT / 'docs/models.md').read_text().split('\n## Profile commands\n')[0]
        policy = policy.replace('[the catalogue](../profiles/catalog.json)', 'the generated profile plans')
        files['.agent-setup/WORKFLOW.md'] = Snapshot(workflow.encode())
        files['.agent-setup/models.md'] = Snapshot((policy + '\n').encode())
        for host in effective['providers']:
            result = profiles.plan(host, requested['profile'], requested['capabilities'].get(host))
            files[f'.agent-setup/profile-{host}.json'] = Snapshot(json_bytes(result))
            for path, content in profiles.native_files(result):
                files[owned_path(path)] = Snapshot(content.encode())
    skill_roots = []
    for name in effective['skills']:
        prefix = f'modules/{accepted[name]["module"]}/skills/{name}'
        package = package_files(ROOT, prefix)
        require('SKILL.md' in package, f'Missing SKILL.md for {name}')
        for host in effective['providers']:
            destination = f'{SKILL_DIR[host]}/{name}'
            skill_roots.append(destination)
            for rel, value in package.items():
                path = owned_path(f'{destination}/{rel}')
                files[path] = Snapshot(value.data, 0o755 if value.mode & 0o111 else 0o644)
    return files, blocks, skill_roots


def block_base(path, current, record):
    body = current.data if current else b''
    if record:
        old = record['text'].encode()
        require(current is not None and body.count(old) == 1
                and body.count(START) == body.count(END) == 1,
                f'Edited or missing managed block: {path}; restore the recorded block or reconcile it manually')
        return body.replace(old, b'', 1), old
    require(START not in body and END not in body,
            f'Unowned instruction markers: {path}; inspect the existing setup')
    return body, None


def imports_agents(body):
    # Recognise standalone imports, not examples inside fenced code.
    fence = None
    for line in body.splitlines():
        marker = line.lstrip()[:3]
        if marker in (b'\x60\x60\x60', b'~~~'):
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
        elif fence is None and line in (b'@AGENTS.md', b'@./AGENTS.md'):
            return True
    return False


def plan_block(path, current, old, payload):
    body, old_block = block_base(path, current, old)
    created = old['created'] if old else current is None
    if path == 'CLAUDE.md' and payload is not None and imports_agents(body):
        payload = None
    mode = current.mode if current else 0o644
    if payload is None:
        after = None if created and not body else Snapshot(body, mode)
        return after, None
    prefix = (b'\n\n' if old_block.startswith(b'\n\n') else b'') if old_block else (
        b'' if current is None else b'\n\n')
    block = prefix + START + b'\n' + payload.rstrip(b'\n') + b'\n' + END + b'\n'
    after = (current.data.replace(old_block, block, 1) if old_block else body + block)
    return Snapshot(after, mode), {'kind': 'block', 'text': block.decode(), 'created': created}


def check_owned(root, files):
    for path, row in files.items():
        current = snapshot(root, path)
        if row['kind'] == 'block':
            block_base(path, current, row)
        else:
            require(fingerprint(current) == {'sha256': row['sha256'], 'mode': row['mode']},
                    f'Edited or missing managed file: {path}; restore its recorded version before proceeding')


def source_version(manifest, files, blocks):
    # Content identity also covers a source archive or uncommitted source changes.
    identity = {'manifest': manifest, 'files': {p: fingerprint(v) for p, v in files.items()},
                'blocks': {p: digest(v) for p, v in blocks.items()}}
    try:
        result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                capture_output=True, text=True, timeout=5, check=True)
        revision = result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        revision = None
    return {'git_commit': revision, 'content_sha256': digest(json_bytes(identity))}


def make_plan(root, args, state):
    old = state['files'] if state else {}
    check_owned(root, old)
    if args.remove:
        require(not any((args.modules, args.providers, args.skills, args.profile,
                         args.codex_capabilities, args.claude_capabilities)),
                '--remove cannot be combined with selection options')
        files, blocks, requested, effective, source, skill_roots = {}, {}, None, None, None, []
    else:
        manifest = read_json(ROOT, 'core/manifest.json')
        require(manifest['schema'] == 1, 'Unsupported source manifest')
        requested, effective, accepted = select(args, state, manifest)
        if 'codex' in effective['providers']:
            require(snapshot(root, 'AGENTS.override.md') is None,
                    'AGENTS.override.md would shadow AGENTS.md; reconcile instructions manually')
        files, blocks, skill_roots = desired_files(requested, effective, accepted)
        source = source_version(manifest, files, blocks)
    # A package must not merge with an unrelated or locally extended skill directory.
    # Check both the previous and the requested selection, including removal.
    for path in old:
        parts = relative(path)
        if len(parts) >= 4 and parts[:2] in (('.agents', 'skills'), ('.claude', 'skills')):
            skill_roots.append('/'.join(parts[:3]))
    for directory in sorted(set(skill_roots)):
        location = safe_path(root, directory, directory=True)
        if location.exists():
            existing = package_files(root, directory)
            for rel in existing:
                require(f'{directory}/{rel}' in old,
                        f'Unowned content in skill directory: {directory}/{rel}; move it or choose another skill')
    changes, ownership = {}, {}
    for path in sorted(set(old) | set(files) | set(blocks)):
        owned_path(path)
        current = snapshot(root, path)
        record = old.get(path)
        if path in INSTRUCTIONS:
            after, row = plan_block(path, current, record, blocks.get(path))
        else:
            after = files.get(path)
            require(record is not None or current is None,
                    f'Unowned file collision: {path}; keep or move the existing file and preview again')
            row = {'kind': 'file', **after.fingerprint()} if after is not None else None
        if row is not None:
            ownership[path] = row
        if current != after:
            changes[path] = (current, after)
    new_state = None if args.remove else {'schema': 1, 'requested': requested, 'effective': effective,
                                         'source': source, 'files': ownership}
    before = snapshot(root, STATE)
    after = Snapshot(json_bytes(new_state), before.mode if before else 0o644) if new_state else None
    if before != after:
        changes[STATE] = (before, after)
    return changes, new_state


def describe(root, changes, state):
    rows = []
    for path, (before, after) in changes.items():
        row = {'path': path, 'action': 'create' if before is None else 'remove' if after is None else 'update',
               'before': fingerprint(before), 'after': fingerprint(after)}
        try:
            a = before.data.decode().splitlines(keepends=True) if before else []
            b = after.data.decode().splitlines(keepends=True) if after else []
            row['diff'] = ''.join(difflib.unified_diff(a, b, fromfile='before/' + path, tofile='after/' + path))
        except UnicodeDecodeError:
            row['diff'] = None
        rows.append(row)
    directories = sorted({parent.relative_to(root).as_posix()
                          for path, (_, after) in changes.items() if after is not None
                          for parent in (root / path).parents if parent != root
                          and root in parent.parents and not parent.exists()})
    report = {'target': str(root), 'directories_to_create': directories,
              'selection': state['effective'] if state else None,
              'requested': state['requested'] if state else None, 'source': state['source'] if state else None,
              'changes': rows}
    # The digest binds the exact reviewed bytes/modes, target and selection.
    report['approval'] = digest(json_bytes(report))
    return report


def write_snapshot(root, path, value, expected):
    require(snapshot(root, path) == expected, f'File changed since preview: {path}')
    target = safe_path(root, path)
    if value is None:
        if expected is not None:
            target.unlink()
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    safe_path(root, path)
    fd, temporary = tempfile.mkstemp(prefix='.agent-setup-write-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(value.data)
            os.fchmod(handle.fileno(), value.mode)
            handle.flush()
            os.fsync(handle.fileno())
        require(snapshot(root, path) == expected, f'File changed while writing: {path}')
        if expected is None:
            # Unlike replace, link fails if an unowned destination appeared.
            os.link(temporary, target)
        else:
            os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(root, changes):
    if not changes:
        return
    journal = {'schema': 1, 'changes': {p: {'before': pack(a), 'after': pack(b)}
                                        for p, (a, b) in changes.items()}}
    pending = Snapshot(json_bytes(journal), 0o600)
    write_snapshot(root, PENDING, pending, None)
    for path, (before, after) in changes.items():
        write_snapshot(root, path, after, before)
    write_snapshot(root, PENDING, None, pending)


def recover(root):
    pending = snapshot(root, PENDING)
    require(pending is not None, 'No pending transaction to recover')
    journal = json.loads(pending.data)
    require(journal['schema'] == 1 and isinstance(journal['changes'], dict)
            and journal['changes'], 'Invalid recovery journal')
    restore = {}
    for path, row in journal['changes'].items():
        owned_path(path)
        before, after = Snapshot.unpack(row['before']), Snapshot.unpack(row['after'])
        current = snapshot(root, path)
        require(current in (before, after), f'Recovery conflict: {path}; preserve all versions and resolve manually')
        if current != before:
            restore[path] = (current, before)
    for path, (current, before) in restore.items():
        write_snapshot(root, path, before, current)
    write_snapshot(root, PENDING, None, pending)
    return {'recovered': sorted(restore), 'target': str(root)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['preview', 'apply', 'status', 'recover'])
    parser.add_argument('--target', required=True)
    parser.add_argument('--modules', help='Comma-separated aps,acs; default aps on first install')
    parser.add_argument('--providers', help='Comma-separated codex,claude-code; default both')
    parser.add_argument('--skills', help='Comma-separated accepted skills, or none')
    parser.add_argument('--profile', choices=['economy', 'balanced', 'quality'])
    parser.add_argument('--codex-capabilities', help='Inventory JSON path or none')
    parser.add_argument('--claude-capabilities', help='Inventory JSON path or none')
    parser.add_argument('--remove', action='store_true', help='Remove only managed content')
    parser.add_argument('--approve', help='Approval digest from the exact preview')
    args = parser.parse_args()
    try:
        root = target_root(args.target)
        require(args.command == 'apply' or args.approve is None, '--approve is only for apply')
        if args.command in ('status', 'recover'):
            require(not any((args.remove, args.modules, args.providers, args.skills, args.profile,
                             args.codex_capabilities, args.claude_capabilities)), 'Selection options require preview/apply')
        with target_lock(root):
            if args.command == 'recover':
                report = recover(root)
            else:
                require(snapshot(root, PENDING) is None,
                        'Pending transaction; run recover before any other operation')
                state = load_state(root)
                if args.command == 'status':
                    if state:
                        check_owned(root, state['files'])
                    report = {'target': str(root), 'installed': state is not None, 'state': state}
                else:
                    changes, next_state = make_plan(root, args, state)
                    report = describe(root, changes, next_state)
                    if args.command == 'apply':
                        require(args.approve == report['approval'],
                                'Approval missing or preview stale; run preview and approve its new digest')
                        apply(root, changes)
                        report['applied'] = True
        print(json.dumps(report, indent=2))
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f'Installation error: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
