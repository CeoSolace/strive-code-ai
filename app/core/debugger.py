# app/core/debugger.py
import re
import ast
from typing import Dict, Any, List, Tuple

def debug(task: Dict[str, Any]) -> Dict[str, Any]:
    code = task.get("code", "")
    lang = task.get("language", "").lower()

    errors: List[Dict] = []
    fixed_code = code

    if lang == "python":
        errors = find_python_errors(code)
    elif lang == "javascript":
        errors = find_js_errors(code)
    elif lang == "c":
        errors = find_c_errors(code)

    if errors:
        fixed_code = apply_python_fixes(code, errors) if lang == "python" else code

    return {
        "errors": errors,
        "fixed_code": fixed_code,
        "diagnosed": len(errors) > 0,
        "language": lang
    }

def find_python_errors(code: str) -> List[Dict]:
    errors = []
    lines = code.split('\n')

    # Syntax checks
    for i, line in enumerate(lines):
        if 'print ' in line and '(' not in line:
            errors.append({"line": i+1, "type": "syntax", "msg": "Use print() with parentheses"})
        if re.search(r'[^<>!=]=[^=]', line) and '==' not in line:
            errors.append({"line": i+1, "type": "logic", "msg": "Possible assignment in condition"})

    # AST parse check
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append({"line": e.lineno, "type": "syntax", "msg": str(e)})

    return errors

def find_js_errors(code: str) -> List[Dict]:
    errors = []
    if 'var ' in code and 'let ' not in code and 'const ' not in code:
        errors.append({"line": 0, "type": "best-practice", "msg": "Prefer let/const over var"})
    return errors

def find_c_errors(code: str) -> List[Dict]:
    return [{"line": 0, "type": "warning", "msg": "C code requires compilation to detect errors"}]

def apply_python_fixes(code: str, errors: List[Dict]) -> str:
    lines = code.split('\n')
    for err in errors:
        if err["type"] == "syntax" and "print(" in err["msg"]:
            line_idx = err["line"] - 1
            if line_idx < len(lines):
                lines[line_idx] = lines[line_idx].replace("print ", "print(").rstrip() + ")"
    return '\n'.join(lines)
