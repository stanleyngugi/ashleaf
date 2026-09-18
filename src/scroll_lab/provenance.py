"""Small reproducibility fingerprints with no third-party dependencies."""

from __future__ import annotations

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

