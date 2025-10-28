# scripts/upgrade.py
#!/usr/bin/env python3
"""
Strive-Code AI Self-Upgrade Orchestrator
Executes system upgrades via git + webhook.
Can be triggered via API or CLI.
"""
import os
import sys
import subprocess
import requests
import json
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WEBHOOK_URL = os.getenv("RENDER_WEBHOOK")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def log(msg: str):
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] [UPGRADE] {msg}")

def commit_upgrade(feature: str, code: str, target_file: str):
    """Write upgrade code and commit to git."""
    file_path = REPO_ROOT / target_file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(code)
    
    log(f"Upgrade code written to {target_file}")
    
    # Git operations
    try:
        subprocess.run(["git", "config", "user.name", "Strive-Code AI"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "config", "user.email", "ai@strive-code.dev"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "add", str(file_path)], cwd=REPO_ROOT, check=True)
        
        commit_msg = f"SELF-UPGRADE: {feature} @ {datetime.datetime.now().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        
        subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)
        log(f"Upgrade committed and pushed: {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git operation failed: {e}")
        return False

def trigger_redeploy():
    """Trigger Render.com redeploy via webhook."""
    if not WEBHOOK_URL:
        log("RENDER_WEBHOOK not set. Skipping redeploy.")
        return False
    
    try:
        response = requests.post(WEBHOOK_URL, timeout=10)
        if response.status_code == 200:
            log("Redeploy webhook triggered successfully.")
            return True
        else:
            log(f"Redeploy webhook failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"Redeploy trigger failed: {e}")
        return False

def create_github_issue(title: str, body: str):
    """Optionally create GitHub issue for tracking."""
    if not GITHUB_TOKEN:
        return
    
    repo = os.getenv("GITHUB_REPO", "strive-code-ai/strive-code-ai")
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body}
    
    try:
        requests.post(url, headers=headers, json=data, timeout=10)
        log("GitHub issue created for upgrade tracking.")
    except:
        pass

def main():
    if len(sys.argv) < 4:
        print("Usage: upgrade.py <feature> <target_file> <code_or_template>")
        sys.exit(1)
    
    feature = sys.argv[1]
    target_file = sys.argv[2]
    code_input = sys.argv[3]
    
    # If code_input is a template name, load from templates
    template_dir = REPO_ROOT / "upgrade_templates"
    if (template_dir / f"{code_input}.py").exists():
        code = (template_dir / f"{code_input}.py").read_text()
    else:
        code = code_input
    
    log(f"Starting upgrade: {feature}")
    
    if commit_upgrade(feature, code, target_file):
        trigger_redeploy()
        create_github_issue(
            f"Self-Upgrade: {feature}",
            f"Automated upgrade applied via `upgrade.py`.\n\nFile: `{target_file}`\nTimestamp: {datetime.datetime.now()}"
        )
        log("UPGRADE CYCLE COMPLETE.")
    else:
        log("UPGRADE FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
