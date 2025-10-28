# app/utils/exec.py
import subprocess
import os
import signal
from typing import Tuple, Optional
import logging

logger = logging.getLogger("strive-code-ai.exec")

def run_command(
    cmd: list,
    cwd: Optional[str] = None,
    timeout: int = 30,
    env: Optional[dict] = None
) -> Tuple[bool, str, str]:
    """
    Execute shell command with timeout and isolation.
    Returns (success, stdout, stderr)
    """
    full_env = {**os.environ, **(env or {})}
    full_env["PATH"] = "/usr/local/bin:/usr/bin:/bin"

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=full_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=os.setsid
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", f"Timeout after {timeout}s")
    except Exception as e:
        return (False, "", f"Execution failed: {e}")

def run_python_code(code: str, timeout: int = 10) -> Tuple[bool, str, str]:
    """Run Python code in isolated subprocess."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    success, out, err = run_command(["python", path], timeout=timeout)
    os.unlink(path)
    return success, out, err

def run_bash_script(script: str, timeout: int = 15) -> Tuple[bool, str, str]:
    """Run bash script."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write("#!/bin/bash\nset -euo pipefail\n")
        f.write(script)
        path = f.name

    os.chmod(path, 0o755)
    success, out, err = run_command(["bash", path], timeout=timeout)
    os.unlink(path)
    return success, out, err

def kill_process_group(pid: int):
    """Kill process and all children."""
    try:
        os.killpg(pid, signal.SIGTERM)
    except:
        pass
