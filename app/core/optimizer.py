# app/core/optimizer.py
import re
from typing import Dict, Any, List

def optimize(task: Dict[str, Any]) -> Dict[str, Any]:
    code = task.get("code", "")
    lang = task.get("language", "").lower()

    original = code
    improvements = []

    if lang == "python":
        code, imp = optimize_python(code)
        improvements.extend(imp)
    elif lang == "javascript":
        code, imp = optimize_js(code)
        improvements.extend(imp)

    return {
        "optimized_code": code,
        "original_code": original,
        "improvements": improvements,
        "savings": len(original) - len(code),
        "language": lang
    }

def optimize_python(code: str) -> tuple[str, List[str]]:
    improvements = []
    lines = code.split('\n')
    cleaned = []

    # Track used variables
    used_vars = set(re.findall(r'\b([a-zA-Z_]\w*)\b', code))
    imports = []

    for line in lines:
        if line.strip().startswith(("import ", "from ")):
            mod = line.split()[1].split('.')[0]
            if mod in used_vars or mod in {"os", "sys", "json", "math"}:
                cleaned.append(line)
                imports.append(mod)
            else:
                improvements.append(f"Removed unused import: {line.strip()}")
        else:
            # Remove pass in non-empty blocks
            if line.strip() == "pass" and not is_empty_block(line, lines):
                improvements.append("Removed unnecessary pass")
            else:
                cleaned.append(line)

    return '\n'.join(cleaned), improvements

def optimize_js(code: str) -> tuple[str, List[str]]:
    improvements = []
    code = re.sub(r'var ', 'let ', code)
    improvements.append("Replaced var with let")
    return code, improvements

def is_empty_block(line: str, lines: List[str]) -> bool:
    return False  # Simplified
