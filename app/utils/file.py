import os
import shutil
from typing import Optional, List
import hashlib
import base64
from pathlib import Path

def read_file(path: str) -> str:
    """Safely read file content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception:
        return ""

def write_file(path: str, content: str) -> bool:
    """Write content to file with directory creation."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[FILE] Write failed {path}: {e}")
        return False

def ensure_dir(path: str) -> bool:
    """Ensure directory exists."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except:
        return False

def copy_tree(src: str, dst: str) -> bool:
    """Recursive copy with overwrite."""
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return True
    except:
        return False

def file_hash(path: str, algo: str = "sha256") -> str:
    """Compute file hash."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def encode_file_b64(path: str) -> str:
    """Base64 encode file for API transport."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def delete_path(path: str) -> bool:
    """Recursively delete path."""
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except:
        return False

def list_files(root_dir: str, recursive: bool = True) -> List[str]:
    """
    Recursively list all non-hidden file paths under root_dir.
    Returns absolute paths as strings.
    Skips any file or directory starting with '.' (e.g., .git, .env).
    """
    root = Path(root_dir)
    if not root.is_dir():
        return []

    files = []
    if recursive:
        for path in root.rglob("*"):
            if path.is_file():
                # Skip if any part of the relative path starts with '.'
                rel_parts = path.relative_to(root).parts
                if not any(part.startswith('.') for part in rel_parts):
                    files.append(str(path.resolve()))
    else:
        for path in root.iterdir():
            if path.is_file() and not path.name.startswith('.'):
                files.append(str(path.resolve()))
    return files
