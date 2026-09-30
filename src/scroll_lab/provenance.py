"""Small reproducibility fingerprints and strict cross-platform text hashes.

FB08's internal freeze records raw SHA-256 of Windows-generated JSON files,
whose text writers emitted CRLF. A clean Unix reproduction emits LF. Accept
only these two newline encodings of otherwise identical bytes; do not weaken
the check to semantic JSON equality or ignore content changes.
"""

from __future__ import annotations

import hashlib
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _git_commit(repo_root: str | Path | None) -> str | None:
    if repo_root is None:
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(repo_root),
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def environment_fingerprint(repo_root: str | Path | None = None) -> dict[str, object]:
    """Return a JSON-serializable run fingerprint."""

    nvidia_smi = shutil.which("nvidia-smi")
    return {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git_commit": _git_commit(repo_root),
        "nvidia_smi_available": nvidia_smi is not None,
    }


def sha256_bytes(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def matches_frozen_text_sha256(path: str | Path, expected: str) -> bool:
    """Match raw bytes or their sole LF/CRLF newline conversion."""

    contents = Path(path).read_bytes()
    if sha256_bytes(contents) == expected:
        return True
    if b"\r\n" in contents:
        converted = contents.replace(b"\r\n", b"\n")
    else:
        converted = contents.replace(b"\n", b"\r\n")
    return sha256_bytes(converted) == expected
