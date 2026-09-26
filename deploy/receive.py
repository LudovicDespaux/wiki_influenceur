#!/usr/bin/python3
"""Restricted SSH receiver: publish static files, never execute uploaded code."""
import fcntl
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
import time
import urllib.request

BASE = Path('/opt/wiki-influenceur')
URL = 'http://127.0.0.1/wiki-influenceur/version.json'
MAX_BYTES = 20 * 1024 * 1024


def unpack(data, destination, commit):
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) > 2000 or sum(m.size for m in members) > 64 * 1024 * 1024:
            raise ValueError('Archive too large')
        seen = set()
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or '\\' in member.name:
                raise ValueError('Unsafe archive path')
            if name == PurePosixPath('.') and member.isdir():
                continue
            if not name.parts or any(p.startswith('.') for p in name.parts):
                raise ValueError('Hidden or empty path')
            if name in seen or not (member.isfile() or member.isdir()):
                raise ValueError('Duplicate path or unsupported entry')
            seen.add(name)
            target = destination / str(name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                target.chmod(0o755)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o644)
    if not (destination / 'index.html').is_file():
        raise ValueError('Missing index.html')
    if json.loads((destination / 'version.json').read_text())['commit'] != commit:
        raise ValueError('Version mismatch')


def activate(release):
    temporary = BASE / 'next'
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(release)
    temporary.replace(BASE / 'current')


def main():
    command = os.environ.get('SSH_ORIGINAL_COMMAND', '')
    match = re.fullmatch(r'deploy ([a-f0-9]{40})', command)
    if not match:
        raise ValueError('Only deploy <commit> is permitted')
    commit = match[1]
    # Refuse a superseded or unmerged revision, including delayed workflows.
    with urllib.request.urlopen('https://api.github.com/repos/LudovicDespaux/wiki_influenceur/git/ref/heads/main', timeout=15) as response:
        if json.load(response)['object']['sha'] != commit:
            raise ValueError('Revision is not current main')
    with (BASE / 'deploy.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Upload too large')
        release = Path(tempfile.mkdtemp(prefix=commit[:12] + '-', dir=BASE / 'releases'))
        release.chmod(0o755)
        try:
            unpack(data, release, commit)
        except Exception:
            shutil.rmtree(release)
            raise
        current = BASE / 'current'
        previous = current.readlink() if current.is_symlink() else None
        activate(release)
        try:
            for attempt in range(10):
                try:
                    request = urllib.request.Request(URL, headers={'Host': '91.134.138.53'})
                    with urllib.request.urlopen(request, timeout=5) as response:
                        if json.load(response)['commit'] == commit:
                            print('Deployed ' + commit)
                            return
                except (OSError, ValueError):
                    pass
                time.sleep(1)
            raise RuntimeError('HTTP verification failed')
        except Exception:
            if previous is None:
                current.unlink(missing_ok=True)
            else:
                activate(previous)
            raise


if __name__ == '__main__':
    main()
