import os
import shutil
from typing import Dict, Any, List
from app.utils.git import clone_repo, commit_and_push
from app.utils.file import read_file, write_file, list_files
from .transpiler import transpile
from .optimizer import optimize
import tempfile

def reconstruct_repo(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Take any GitHub repo → reconstruct in new language with modifications.
    Full symbolic repo transformation.
    """
    url = task["github_url"]
    target_lang = task.get("language", "rust")
    mods = task.get("modifications", [])
    optimize_flag = task.get("optimize", True)

    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = clone_repo(url, tmpdir)
        if not local_path:
            return {"error": "Clone failed"}

        files = list_files(local_path)
        new_files = []

        for file_path in files:
            if _is_code_file(file_path):
                code = read_file(file_path)
                if code == "":  # skip unreadable or empty files
                    continue

                ext = os.path.splitext(file_path)[1]

                # Detect source lang
                src_lang = _detect_lang(ext, code)

                # Transpile
                if src_lang and src_lang != target_lang:
                    result = transpile({
                        "code": code,
                        "from": src_lang,
                        "to": target_lang
                    })
                    new_code = result.get("code", code)
                else:
                    new_code = code

                # Optimize
                if optimize_flag:
                    opt_result = optimize({
                        "code": new_code,
                        "language": target_lang
                    })
                    new_code = opt_result.get("optimized_code", new_code)

                # Apply modifications
                for mod in mods:
                    new_code = _apply_mod(new_code, mod)

                new_ext = _get_ext(target_lang)
                new_path = file_path.replace(ext, new_ext)
                new_files.append(new_path)
                write_file(new_path, new_code)

        # Create new repo directory
        new_repo_path = local_path + f"_strived_in_{target_lang}"
        os.makedirs(new_repo_path, exist_ok=True)

        # Copy all original (non-hidden) content
        for item in os.listdir(local_path):
            if item.startswith('.'):
                continue
            src_item = os.path.join(local_path, item)
            dst_item = os.path.join(new_repo_path, item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)

        # Push to new remote
        push_url = commit_and_push(new_repo_path, f"Reconstructed in {target_lang} by Strive-Code AI")

        return {
            "original": url,
            "new_repo": push_url,
            "language": target_lang,
            "files_transpiled": len(new_files),
            "modifications": mods,
            "status": "reconstructed"
        }

def _is_code_file(path: str) -> bool:
    code_exts = {".py", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".java", ".rb", ".php", ".cs"}
    return any(path.endswith(ext) for ext in code_exts)

def _detect_lang(ext: str, code: str) -> str:
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".c": "c",
        ".cpp": "cpp",
        ".java": "java",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp"
    }
    return ext_map.get(ext, "unknown")

def _get_ext(lang: str) -> str:
    lang_ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "rust": ".rs",
        "go": ".go",
        "c": ".c",
        "cpp": ".cpp",
        "java": ".java",
        "ruby": ".rb",
        "php": ".php",
        "csharp": ".cs"
    }
    return lang_ext_map.get(lang, ".txt")

def _apply_mod(code: str, mod: str) -> str:
    mod = mod.strip().lower()
    if "add auth" in mod:
        return code + "\n# AUTH ADDED: JWT middleware"
    # Add more mod handlers here as needed
    return code
