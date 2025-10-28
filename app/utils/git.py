# app/utils/git.py
import os
import shutil
import subprocess
from typing import Optional, List
import git
from git.exc import GitCommandError
import logging

logger = logging.getLogger("strive-code-ai.git")

def clone_repo(url: str, dest: Optional[str] = None) -> Optional[str]:
    """
    Clone public GitHub repo to local path.
    Returns local directory path.
    """
    if not url.startswith("https://github.com/"):
        logger.error(f"[GIT] Invalid GitHub URL: {url}")
        return None

    repo_name = url.split("/")[-1].replace(".git", "")
    clone_path = dest or f"/tmp/{repo_name}_{os.urandom(4).hex()}"

    try:
        git.Repo.clone_from(url, clone_path, depth=1)
        logger.info(f"[GIT] Cloned {url} → {clone_path}")
        return clone_path
    except GitCommandError as e:
        logger.error(f"[GIT] Clone failed: {e}")
        return None

def commit_and_push(local_path: str, commit_msg: str, remote: str = "origin") -> Optional[str]:
    """
    Commit all changes and push to remote.
    Returns public URL if successful.
    """
    try:
        repo = git.Repo(local_path)
        repo.git.add(A=True)
        repo.index.commit(commit_msg)
        origin = repo.remote(name=remote)
        push_info = origin.push()[0]
        if push_info.flags & push_info.ERROR:
            return None
        return repo.remotes.origin.url.replace(".git", "")
    except Exception as e:
        logger.error(f"[GIT] Push failed: {e}")
        return None

def create_repo_from_scratch(name: str, private: bool = False) -> Optional[str]:
    """
    Create new GitHub repo via API (requires GITHUB_TOKEN).
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None

    import requests
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {"name": name, "private": private, "auto_init": True}
    resp = requests.post("https://api.github.com/user/repos", json=data, headers=headers)
    if resp.status_code == 201:
        return resp.json()["html_url"]
    return None

def list_files(path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Recursively list files in directory, optionally filtered by extension.
    """
    matches = []
    for root, _, files in os.walk(path):
        for f in files:
            fpath = os.path.join(root, f)
            if extensions:
                if any(fpath.endswith(ext) for ext in extensions):
                    matches.append(fpath)
            else:
                matches.append(fpath)
    return matches
